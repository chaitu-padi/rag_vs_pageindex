"""
Comparison UI for PageIndex RAG vs Standard RAG.
Provides both CLI and web-based comparison tools.
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from typing import Tuple, Dict, List
import asyncio

# Add parent directory to path for imports to work when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import web dependencies, make them optional
try:
    from flask import Flask, render_template, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

from pageindex.page_index import page_index_main
from pageindex.standard_rag import StandardRAG
from pageindex.utils import ChatGPT_API, ChatGPT_API_async, OPEN_API_KEY, extract_json

logger = logging.getLogger(__name__)


def run_async_in_thread(coro):
    """
    Run an async coroutine in a new thread with its own event loop.
    This is safe to call from synchronous Flask contexts.
    """
    result = [None]
    exception = [None]

    def run_in_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result[0] = loop.run_until_complete(coro)
            finally:
                loop.close()
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=run_in_thread, daemon=False)
    thread.start()
    thread.join()

    if exception[0]:
        raise exception[0]
    return result[0]


class PageIndexTreeSearch:
    """Perform tree search and retrieval on PageIndex document structure."""

    def __init__(self, tree_structure, pdf_path: str, model_name: str = "gpt-4o-2024-11-20"):
        """
        Initialize tree search with PageIndex structure.

        Args:
            tree_structure: The hierarchical tree structure from PageIndex
            pdf_path: Path to the original PDF
            model_name: LLM model to use for reasoning
        """
        self.tree_structure = tree_structure
        self.pdf_path = pdf_path
        self.model_name = model_name
        self.pdf_text = self._extract_pdf_text()

    def _extract_pdf_text(self) -> str:
        """Extract text from PDF for context retrieval."""
        try:
            import pymupdf
            doc = pymupdf.open(self.pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""

    def _flatten_tree(self, nodes, depth=0) -> List[Dict]:
        """Flatten tree structure into list for easier traversal."""
        flattened = []
        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            node_copy = {
                "depth": depth,
                "title": node.get("title", ""),
                "summary": node.get("summary", ""),
                "page_num": node.get("page_num") or node.get("physical_index", 0),
            }
            flattened.append(node_copy)

            # Recursively flatten child nodes
            if "nodes" in node and node["nodes"]:
                flattened.extend(self._flatten_tree(node["nodes"], depth + 1))

        return flattened

    def retrieve_relevant_sections(self, query: str, top_k: int = 5) -> Tuple[List[Dict], str]:
        """
        Use LLM reasoning to identify relevant sections in the tree.

        Args:
            query: User query
            top_k: Number of top relevant sections to retrieve

        Returns:
            Tuple of (relevant sections, reasoning explanation)
        """
        # Flatten tree for easier evaluation
        flattened_nodes = self._flatten_tree(self.tree_structure)

        if not flattened_nodes:
            return [], "No sections found in document"

        # Create a concise representation of the document structure
        structure_text = "Document Structure:\n"
        for i, node in enumerate(flattened_nodes[:100]):  # Increased limit to better coverage
            indent = "  " * node["depth"]
            summary = node["summary"] if node["summary"] else "(No summary available)"
            # Truncate summary for clarity
            summary_short = summary[:80] if summary else "(No summary)"
            structure_text += f"{indent}[{i}] {node['title']} (p.{node['page_num']}) - {summary_short}...\n"

        # Use LLM to reason about which sections are relevant
        reasoning_prompt = f"""You are an expert document analyst. Given the following query and document structure, identify which sections would contain relevant information to answer the query.

The document is organized hierarchically with deeper indentation indicating subsections.

Query: {query}

{structure_text}

Task: List the indices of the top {top_k} most relevant sections that would likely contain information to answer the query. Consider:
1. Direct topic match (title contains key terms)
2. Hierarchical context (parent sections that provide framing)
3. Related concepts that help answer the question comprehensively
4. Cross-references between sections

For each section, explain briefly why it's relevant.

Response format (JSON):
{{
    "reasoning": "Your explanation of why you selected these sections and how they connect to answer the query",
    "relevant_indices": [index1, index2, ...],
    "confidence": 0.0-1.0
}}

Return ONLY valid JSON."""

        try:
            response = ChatGPT_API(model=self.model_name, prompt=reasoning_prompt)
            result = extract_json(response)
            relevant_indices = result.get("relevant_indices", [])[:top_k]
            reasoning = result.get("reasoning", "")

            # Retrieve the actual sections
            relevant_sections = [flattened_nodes[i] for i in relevant_indices if i < len(flattened_nodes)]
            
            # Fallback: if no sections retrieved, get top sections by position
            if not relevant_sections:
                logger.warning(f"No relevant sections found via reasoning, using fallback")
                relevant_sections = flattened_nodes[:top_k]

            return relevant_sections, reasoning

        except Exception as e:
            logger.error(f"Error in tree search reasoning: {e}")
            # Fallback: return top sections by position
            return flattened_nodes[:top_k], f"Error during reasoning: {e}"

    def generate_answer(self, query: str, relevant_sections: List[Dict], reasoning: str) -> Dict:
        """
        Generate answer based on retrieved sections using LLM.

        Args:
            query: User query
            relevant_sections: List of relevant sections retrieved
            reasoning: Reasoning explanation from retrieval

        Returns:
            Dictionary with answer and metadata
        """
        if not relevant_sections:
            return {
                "answer": "No relevant sections found in the document to answer this query.",
                "num_sections_retrieved": 0,
                "reasoning": "Empty section list"
            }

        # Create context from retrieved sections with better structure
        context = f"Based on the document structure analysis, here are the relevant sections:\n\n"
        for idx, section in enumerate(relevant_sections, 1):
            context += f"{idx}. **{section['title']}** (Page {section['page_num']})\n"
            if section['summary']:
                context += f"   Summary: {section['summary']}\n"
            context += "\n"

        # Generate answer using LLM with multi-step reasoning prompt
        answer_prompt = f"""You are a professional document analyst with expertise in extracting insights from structured documents.

Your task is to answer the following query comprehensively by synthesizing information from relevant sections of a document.

User Query: {query}

Retrieved Sections:
{context}

Analysis Guidance:
- This query may require synthesizing information across multiple sections
- Look for explicit statements, examples, and implicit connections
- If sections discuss related concepts, explain how they relate to answer the query
- Provide specific details and citations where relevant
- If information is insufficient, note what additional details would help

Please provide a comprehensive, well-reasoned answer that synthesizes the information from the retrieved sections."""

        try:
            answer = ChatGPT_API(model=self.model_name, prompt=answer_prompt)
            return {
                "answer": answer,
                "num_sections_retrieved": len(relevant_sections),
                "retrieved_sections": [s["title"] for s in relevant_sections],
                "reasoning": reasoning,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": f"Error generating answer: {e}",
                "num_sections_retrieved": len(relevant_sections),
                "status": "error"
            }


class RAGComparator:
    """Compare PageIndex RAG and Standard RAG systems."""


    def __init__(self, pdf_path: str):
        """
        Initialize comparator with a PDF.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = pdf_path
        self.pdf_name = Path(pdf_path).name
        self.pageindex_rag = None
        self.standard_rag = None
        self.comparison_results = []

    def setup_standard_rag(self, progress_callback=None) -> None:
        """Initialize the Standard RAG system with progress logging and batch progress forwarding."""
        logger.info("[Standard RAG] Starting setup...")
        print("[Standard RAG] Starting setup...", flush=True)
        if progress_callback:
            progress_callback("Standard RAG: Initializing...")
        self.standard_rag = StandardRAG(
            model_name="gpt-4o-2024-11-20",
            chunk_size=512,
            chunk_overlap=100,
            top_k=3
        )
        logger.info("[Standard RAG] Ingesting PDF...")
        print("[Standard RAG] Ingesting PDF...", flush=True)
        if progress_callback:
            progress_callback("Standard RAG: Ingesting PDF...")
        # Wrap the original progress callback to forward batch progress
        def batch_progress_callback(msg):
            logger.info(f"[Standard RAG] {msg}")
            print(f"[Standard RAG] {msg}", flush=True)  # Print to terminal for visibility
            if progress_callback:
                progress_callback(f"Standard RAG: {msg}")
        self.standard_rag.ingest_pdf(self.pdf_path, progress_callback=batch_progress_callback)
        logger.info("[Standard RAG] Setup complete.")
        print("[Standard RAG] Setup complete.", flush=True)
        if progress_callback:
            progress_callback("Standard RAG: Setup complete.")

    def setup_pageindex_rag_sync(self, progress_callback=None) -> None:
        """Synchronous initialization for PageIndex RAG with progress logging and structure validation."""
        logger.info("[PageIndex RAG] Starting setup...")
        if progress_callback:
            progress_callback("PageIndex RAG: Initializing...")
        
        try:
            # Create a simple options object with required attributes
            class PageIndexOptions:
                def __init__(self):
                    self.model = "gpt-4o-2024-11-20"
                    self.toc_check_page_num = 20  # Check up to 20 pages for table of contents
                    self.max_page_num_each_node = 15  # Max pages per node before splitting
                    self.max_token_num_each_node = 4000  # Max tokens per node
                    self.if_add_node_id = "yes"
                    self.if_add_node_text = "yes"
                    self.if_add_node_summary = "yes"  # Enable summaries for better retrieval
                    self.if_add_doc_description = "no"
            
            opt = PageIndexOptions()
            logger.info(f"[PageIndex RAG] Options configured: toc_check_page_num={opt.toc_check_page_num}, max_page_num_each_node={opt.max_page_num_each_node}")
            if progress_callback:
                progress_callback("PageIndex RAG: Parsing PDF (this may take a moment)...")
            
            self.pageindex_rag = page_index_main(self.pdf_path, opt=opt)
        except TypeError as e:
            logger.error(f"[PageIndex RAG] Type error during parsing: {type(e).__name__}: {e}")
            if progress_callback:
                progress_callback(f"PageIndex RAG: Type error - {str(e)[:80]}")
            # Try again with minimal options
            try:
                logger.info("[PageIndex RAG] Retrying with minimal options...")
                if progress_callback:
                    progress_callback("PageIndex RAG: Retrying with minimal options...")
                
                class MinimalPageIndexOptions:
                    def __init__(self):
                        self.model = "gpt-4o-2024-11-20"
                        self.toc_check_page_num = 10  # Very conservative
                        self.max_page_num_each_node = 10  # Smaller nodes
                        self.max_token_num_each_node = 2000  # Fewer tokens
                        self.if_add_node_id = "yes"
                        self.if_add_node_text = "no"  # Disable text extraction
                        self.if_add_node_summary = "yes"  # Keep summaries for retrieval
                        self.if_add_doc_description = "no"
                
                opt = MinimalPageIndexOptions()
                self.pageindex_rag = page_index_main(self.pdf_path, opt=opt)
            except Exception as e2:
                logger.error(f"[PageIndex RAG] Retry also failed: {type(e2).__name__}: {e2}")
                if progress_callback:
                    progress_callback(f"PageIndex RAG: Retry failed - {str(e2)[:80]}")
                raise Exception(f"PageIndex RAG parsing failed: {str(e)} (retry: {str(e2)})")
        except Exception as e:
            logger.error(f"[PageIndex RAG] page_index_main failed: {type(e).__name__}: {e}")
            if progress_callback:
                progress_callback(f"PageIndex RAG: Parsing error - {str(e)[:100]}")
            raise Exception(f"PageIndex RAG parsing failed: {str(e)}")
        
        # Check if result is None
        if self.pageindex_rag is None:
            logger.error("PageIndex RAG returned None. PDF may be invalid or parsing failed.")
            if progress_callback:
                progress_callback("PageIndex RAG: PDF parsing returned None.")
            raise Exception("PageIndex RAG: PDF parsing returned None - invalid or unsupported PDF format.")
        
        # Get structure info safely
        struct_info = "Unknown"
        structure = None
        try:
            if isinstance(self.pageindex_rag, dict):
                if 'structure' in self.pageindex_rag:
                    structure = self.pageindex_rag['structure']
                    struct_info = f"dict with structure"
                else:
                    struct_info = f"dict with {len(self.pageindex_rag)} keys"
            elif isinstance(self.pageindex_rag, list):
                structure = self.pageindex_rag
                struct_info = f"list with {len(self.pageindex_rag)} items"
            else:
                struct_info = type(self.pageindex_rag).__name__
        except Exception as e:
            logger.error(f"Error inspecting structure: {e}")
        
        logger.info(f"[PageIndex RAG] PDF parsed. Structure: {struct_info}")
        if progress_callback:
            progress_callback("PageIndex RAG: PDF parsed successfully.")
        
        try:
            logger.info("[PageIndex RAG] Initializing tree search...")
            if progress_callback:
                progress_callback("PageIndex RAG: Initializing tree search...")
            
            # Use the structure for tree search, not the entire result
            if structure is None:
                structure = self.pageindex_rag
            
            self.pageindex_searcher = PageIndexTreeSearch(structure, self.pdf_path)
            logger.info("[PageIndex RAG] Setup complete.")
            if progress_callback:
                progress_callback("PageIndex RAG: Setup complete.")
        except Exception as e:
            logger.error(f"PageIndex RAG tree search initialization error: {type(e).__name__}: {e}")
            if progress_callback:
                progress_callback(f"PageIndex RAG: Tree search error - {str(e)[:100]}")
            raise Exception(f"PageIndex RAG: Tree search initialization failed: {str(e)}")

    def compare_query(self, query: str) -> Dict:
        """
        Execute query on both RAG systems and compare results.

        Args:
            query: User query

        Returns:
            Comparison results dictionary
        """
        result = {
            "query": query,
            "timestamp": time.time(),
            "systems": {}
        }

        # === Standard RAG ===
        print("\n[Standard RAG]")
        start_time = time.time()
        try:
            response, retrieved_chunks = self.standard_rag.generate_response(
                query,
                api_key=OPEN_API_KEY
            )
            elapsed = time.time() - start_time

            result["systems"]["standard_rag"] = {
                "response": response,
                "retrieved_chunks": retrieved_chunks,
                "num_chunks_retrieved": len(retrieved_chunks),
                "tokens_used": len(response.split()),  # Rough estimate
                "execution_time_seconds": elapsed,
                "status": "success"
            }
            print(f"✓ Retrieved {len(retrieved_chunks)} chunks in {elapsed:.2f}s")
            print(f"Response: {response[:100]}...")

        except Exception as e:
            logger.error(f"Standard RAG error: {e}")
            result["systems"]["standard_rag"] = {
                "error": str(e),
                "status": "error"
            }
            print(f"✗ Error: {e}")

        # === PageIndex RAG ===
        # Use tree search to retrieve relevant sections and generate answer
        print("\n[PageIndex RAG]")
        start_time = time.time()
        try:
            # Perform tree search to find relevant sections
            relevant_sections, reasoning = self.pageindex_searcher.retrieve_relevant_sections(
                query,
                top_k=5
            )

            # Generate answer based on retrieved sections
            pageindex_result = self.pageindex_searcher.generate_answer(
                query,
                relevant_sections,
                reasoning
            )

            elapsed = time.time() - start_time

            result["systems"]["pageindex_rag"] = {
                "response": pageindex_result.get("answer", ""),
                "num_sections_retrieved": pageindex_result.get("num_sections_retrieved", 0),
                "retrieved_sections": pageindex_result.get("retrieved_sections", []),
                "reasoning": pageindex_result.get("reasoning", ""),
                "execution_time_seconds": elapsed,
                "tokens_used": len(pageindex_result.get("answer", "").split()),  # Rough estimate
                "status": pageindex_result.get("status", "success")
            }
            print(f"✓ Retrieved {pageindex_result.get('num_sections_retrieved', 0)} sections in {elapsed:.2f}s")
            print(f"Response: {pageindex_result.get('answer', '')[:100]}...")

        except Exception as e:
            logger.error(f"PageIndex RAG error: {e}")
            result["systems"]["pageindex_rag"] = {
                "error": str(e),
                "status": "error"
            }
            print(f"✗ Error: {e}")

        self.comparison_results.append(result)
        return result

    def get_comparison_summary(self) -> Dict:
        """
        Get summary statistics of all comparisons.

        Returns:
            Summary dictionary
        """
        if not self.comparison_results:
            return {"message": "No comparisons have been made yet"}

        summary = {
            "pdf": self.pdf_name,
            "total_queries": len(self.comparison_results),
            "standard_rag": {
                "avg_execution_time": 0,
                "avg_chunks_retrieved": 0,
                "success_rate": 0
            },
            "pageindex_rag": {
                "avg_execution_time": 0,
                "avg_sections_retrieved": 0,
                "success_rate": 0,
                "structure_size": 0
            }
        }

        # Calculate Standard RAG statistics
        standard_successful_queries = 0
        standard_total_time = 0
        standard_total_chunks = 0

        # Calculate PageIndex RAG statistics
        pageindex_successful_queries = 0
        pageindex_total_time = 0
        pageindex_total_sections = 0

        for result in self.comparison_results:
            # Standard RAG statistics
            if "standard_rag" in result["systems"]:
                rag_result = result["systems"]["standard_rag"]
                if rag_result.get("status") == "success":
                    standard_successful_queries += 1
                    standard_total_time += rag_result.get("execution_time_seconds", 0)
                    standard_total_chunks += rag_result.get("num_chunks_retrieved", 0)

            # PageIndex RAG statistics
            if "pageindex_rag" in result["systems"]:
                pi_result = result["systems"]["pageindex_rag"]
                if pi_result.get("status") == "success":
                    pageindex_successful_queries += 1
                    pageindex_total_time += pi_result.get("execution_time_seconds", 0)
                    pageindex_total_sections += pi_result.get("num_sections_retrieved", 0)

        # Calculate averages
        if standard_successful_queries > 0:
            summary["standard_rag"]["avg_execution_time"] = standard_total_time / standard_successful_queries
            summary["standard_rag"]["avg_chunks_retrieved"] = standard_total_chunks / standard_successful_queries
            summary["standard_rag"]["success_rate"] = standard_successful_queries / len(self.comparison_results)

        if pageindex_successful_queries > 0:
            summary["pageindex_rag"]["avg_execution_time"] = pageindex_total_time / pageindex_successful_queries
            summary["pageindex_rag"]["avg_sections_retrieved"] = pageindex_total_sections / pageindex_successful_queries
            summary["pageindex_rag"]["success_rate"] = pageindex_successful_queries / len(self.comparison_results)

        # PageIndex structure size
        if self.pageindex_rag:
            summary["pageindex_rag"]["structure_size"] = self._count_nodes(self.pageindex_rag)

        return summary

    @staticmethod
    def _count_nodes(structure) -> int:
        """Recursively count nodes in structure."""
        if isinstance(structure, list):
            count = len(structure)
            for item in structure:
                count += RAGComparator._count_nodes(item.get("nodes", []))
            return count
        elif isinstance(structure, dict):
            return 1 + RAGComparator._count_nodes(structure.get("nodes", []))
        return 0

    def export_results(self, output_path: str) -> None:
        """
        Export comparison results to JSON.

        Args:
            output_path: Path to save results
        """
        export_data = {
            "pdf": self.pdf_name,
            "comparison_results": self.comparison_results,
            "summary": self.get_comparison_summary()
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Results exported to {output_path}")


class CLIComparator:
    """Command-line interface for RAG comparison."""

    @staticmethod
    def get_available_pdfs() -> List[str]:
        """Get list of available test PDFs."""
        pdf_dir = Path("tests/pdfs")
        if not pdf_dir.exists():
            return []
        return [str(p) for p in pdf_dir.glob("*.pdf")]

    @staticmethod
    async def run_interactive():
        """Run interactive comparison mode."""
        print("\n" + "="*60)
        print("RAG COMPARISON TOOL - Interactive Mode")
        print("="*60)

        # Get available PDFs
        pdfs = CLIComparator.get_available_pdfs()

        if not pdfs:
            print("No PDF files found in tests/pdfs/")
            return

        print("\nAvailable PDFs:")
        for i, pdf in enumerate(pdfs, 1):
            print(f"  {i}. {Path(pdf).name}")

        # Select PDF
        try:
            choice = int(input("\nSelect a PDF (number): "))
            if 1 <= choice <= len(pdfs):
                pdf_path = pdfs[choice - 1]
            else:
                print("Invalid selection")
                return
        except ValueError:
            print("Invalid input")
            return

        # Initialize comparator
        print(f"\nInitializing RAG systems for {Path(pdf_path).name}...")
        comparator = RAGComparator(pdf_path)

        # Define progress callback for CLI to print progress with real-time flushing
        def cli_progress_callback(msg):
            print(f"  {msg}", flush=True)

        print("Setting up Standard RAG...")
        comparator.setup_standard_rag(progress_callback=cli_progress_callback)

        print("Setting up PageIndex RAG...")
        comparator.setup_pageindex_rag_sync(progress_callback=cli_progress_callback)

        print("\n" + "="*60)
        print("Ready to compare. Enter queries or type 'quit' to exit.")
        print("="*60 + "\n")

        # Interactive query loop
        while True:
            query = input("\nQuery: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                break

            if not query:
                continue

            print("\nExecuting queries on both systems...")
            result = comparator.compare_query(query)

            # Display comparison
            print("\n" + "-"*60)
            print("COMPARISON RESULTS")
            print("-"*60)

            if "standard_rag" in result["systems"]:
                std_result = result["systems"]["standard_rag"]
                if std_result.get("status") == "success":
                    print(f"\nStandard RAG Response:")
                    print(f"  Time: {std_result['execution_time_seconds']:.2f}s")
                    print(f"  Chunks Retrieved: {std_result['num_chunks_retrieved']}")
                    print(f"  Answer: {std_result['response'][:200]}...")

            print(f"\nPageIndex RAG:")
            print(f"  Document Structure: {result['systems']['pageindex_rag'].get('status', 'unknown')}")

        # Save results
        output_file = f"comparison_results_{Path(pdf_path).stem}.json"
        comparator.export_results(output_file)
        print(f"\nResults saved to {output_file}")

        # Display summary
        summary = comparator.get_comparison_summary()
        print("\n" + "="*60)
        print("COMPARISON SUMMARY")
        print("="*60)
        print(json.dumps(summary, indent=2, default=str))


if HAS_FLASK:
    class WebComparator:
        """Web interface for RAG comparison."""

        def __init__(self):
            self.app = Flask(__name__)
            self.comparators: Dict[str, RAGComparator] = {}
            self.setup_routes()

        def setup_routes(self):
            """Setup Flask routes."""

            @self.app.route("/")
            def index():
                return self.render_index()

            @self.app.route("/api/pdfs", methods=["GET"])
            def get_pdfs():
                pdfs = CLIComparator.get_available_pdfs()
                return jsonify({
                    "pdfs": [{"path": p, "name": Path(p).name} for p in pdfs]
                })

            @self.app.route("/api/init", methods=["POST"])
            def init_rag():
                data = request.json
                pdf_path = data.get("pdf_path")

                if not pdf_path or not Path(pdf_path).exists():
                    return jsonify({"error": "Invalid PDF path"}), 400

                try:
                    # Use streaming endpoint - return a URL for the client to connect to
                    session_id = Path(pdf_path).stem + f"_{int(time.time() * 1000)}"
                    # Store PDF path for streaming endpoint to use
                    self._init_queue = {"pdf_path": pdf_path, "session_id": session_id}
                    return jsonify({
                        "status": "streaming",
                        "stream_url": f"/api/init-stream?session_id={session_id}"
                    })
                except Exception as e:
                    logger.error(f"Initialization error: {e}")
                    return jsonify({"error": str(e)}), 500

            @self.app.route("/api/init-stream")
            def init_stream():
                session_id = request.args.get("session_id")
                if not hasattr(self, "_init_queue") or self._init_queue is None:
                    return "data: {\"error\": \"Invalid session\"}\n\n", 400

                pdf_path = self._init_queue["pdf_path"]
                
                def generate():
                    try:
                        progress_messages = []
                        def progress_callback(msg):
                            logger.info(f"[Progress] {msg}")
                            progress_messages.append(msg)
                            # Send progress update immediately via SSE
                            yield f'data: {json.dumps({"progress": msg, "status": "initializing"})}\n\n'

                        comparator = RAGComparator(pdf_path)
                        yield f'data: {json.dumps({"progress": "Standard RAG: Initializing...", "status": "initializing"})}\n\n'
                        comparator.setup_standard_rag(progress_callback=progress_callback)

                        yield f'data: {json.dumps({"progress": "PageIndex RAG: Initializing...", "status": "initializing"})}\n\n'
                        # Setup PageIndex RAG synchronously
                        try:
                            comparator.setup_pageindex_rag_sync(progress_callback=progress_callback)
                        except Exception as e:
                            logger.error(f"PageIndex RAG sync setup failed: {e}")
                            yield f'data: {json.dumps({"error": str(e), "status": "error"})}\n\n'
                            return

                        # Success - store comparator and return success
                        self.comparators[session_id] = comparator
                        yield f'data: {json.dumps({"status": "initialized", "session_id": session_id, "pdf_name": Path(pdf_path).name})}\n\n'
                    except Exception as e:
                        logger.error(f"Initialization error: {e}")
                        yield f'data: {json.dumps({"error": str(e), "status": "error"})}\n\n'

                return self.app.response_class(
                    generate(),
                    mimetype="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Accel-Buffering": "no"
                    }
                )

            @self.app.route("/api/compare", methods=["POST"])
            def compare():
                data = request.json
                session_id = data.get("session_id")
                query = data.get("query")

                if not session_id or session_id not in self.comparators:
                    return jsonify({"error": "Invalid session"}), 400

                comparator = self.comparators[session_id]

                try:
                    # Run comparison (now synchronous)
                    result = comparator.compare_query(query)
                    return jsonify(result)
                except Exception as e:
                    return jsonify({"error": str(e)}), 500

            @self.app.route("/api/summary/<session_id>", methods=["GET"])
            def get_summary(session_id):
                if session_id not in self.comparators:
                    return jsonify({"error": "Invalid session"}), 400

                summary = self.comparators[session_id].get_comparison_summary()
                return jsonify(summary)

        def render_index(self):
            """Render HTML interface."""
            html = r"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>RAG Comparison Tool</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 1400px;
                        margin: 0 auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    .container {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                    }
                    .panel {
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .control-panel {
                        grid-column: 1 / -1;
                    }
                    h1 { color: #333; }
                    h2 { color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
                    .form-group {
                        margin: 15px 0;
                    }
                    label { display: block; font-weight: bold; margin-bottom: 5px; }
                    select, input, textarea {
                        width: 100%;
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-family: Arial, sans-serif;
                    }
                    textarea { resize: vertical; min-height: 100px; }
                    button {
                        background: #007bff;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                    }
                    button:hover { background: #0056b3; }
                    .result {
                        background: #f9f9f9;
                        padding: 15px;
                        border-left: 4px solid #007bff;
                        margin: 10px 0;
                        border-radius: 4px;
                    }
                    .status { color: #28a745; font-weight: bold; }
                    .error { color: #dc3545; }
                    .loading { color: #ffc107; }
                    .metadata { color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <h1>🔍 RAG Comparison Tool</h1>
                <p>Compare PageIndex RAG vs Standard RAG on PDF documents</p>

                <div class="control-panel panel">
                    <h2>Setup</h2>
                    <div class="form-group">
                        <label>Select PDF:</label>
                        <select id="pdfSelect">
                            <option value="">Loading PDFs...</option>
                        </select>
                    </div>
                    <button onclick="initRAG()">Initialize RAG Systems</button>
                    <div id="initStatus"></div>
                </div>

                <div id="compareSection" style="display: none;">
                    <div class="control-panel panel">
                        <h2>Query</h2>
                        <div class="form-group">
                            <label>Your Question:</label>
                            <textarea id="queryInput" placeholder="Enter your question..."></textarea>
                        </div>
                        <button onclick="executeComparison()">Compare Systems</button>
                        <div id="queryStatus"></div>
                    </div>

                    <div class="container">
                        <div class="panel">
                            <h2>📊 Standard RAG</h2>
                            <div id="standardResult"></div>
                        </div>
                        <div class="panel">
                            <h2>🌳 PageIndex RAG</h2>
                            <div id="pageindexResult"></div>
                        </div>
                    </div>

                    <div class="control-panel panel">
                        <h2>Summary Statistics</h2>
                        <div id="summary"></div>
                    </div>
                </div>

                <script>
                    let currentSessionId = null;

                    async function loadPDFs() {
                        const response = await fetch('/api/pdfs');
                        const data = await response.json();
                        const select = document.getElementById('pdfSelect');
                        select.innerHTML = '';
                        data.pdfs.forEach(pdf => {
                            const option = document.createElement('option');
                            option.value = pdf.path;
                            option.textContent = pdf.name;
                            select.appendChild(option);
                        });
                    }

                    async function initRAG() {
                        const pdfPath = document.getElementById('pdfSelect').value;
                        if (!pdfPath) {
                            alert('Please select a PDF');
                            return;
                        }

                        const statusDiv = document.getElementById('initStatus');
                        statusDiv.innerHTML = '<p class="loading">Initializing...</p>';

                        try {
                            // Start initialization and get stream URL
                            const initResponse = await fetch('/api/init', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ pdf_path: pdfPath })
                            });

                            const initData = await initResponse.json();
                            if (!initData.stream_url) {
                                statusDiv.innerHTML = `<p class="error">Error: ${initData.error}</p>`;
                                return;
                            }

                            // Connect to SSE stream for real-time progress
                            const eventSource = new EventSource(initData.stream_url);
                            let progressMessages = [];
                            let currentBatchPercent = 0;

                            eventSource.onmessage = (event) => {
                                const data = JSON.parse(event.data);

                                if (data.error) {
                                    statusDiv.innerHTML = `<p class="error">Error: ${data.error}</p>`;
                                    eventSource.close();
                                    return;
                                }

                                if (data.status === 'initialized') {
                                    // Initialization complete
                                    currentSessionId = data.session_id;
                                    statusDiv.innerHTML = `<p class="status">✓ Ready: ${data.pdf_name}</p>`;
                                    document.getElementById('compareSection').style.display = 'block';
                                    eventSource.close();
                                    return;
                                }

                                if (data.progress) {
                                    progressMessages.push(data.progress);

                                    // Render progress bar and messages
                                    let progressBar = '';
                                    let progressMsgs = progressMessages.map((msg) => {
                                        if (msg.includes('Batches:')) {
                                            const match = msg.match(/Batches: (\\d+)%\\|/);
                                            if (match) {
                                                const percent = parseInt(match[1]);
                                                currentBatchPercent = percent;
                                                progressBar = `<div style="margin:8px 0; width:100%; background:#eee; border-radius:4px; height:20px;">
                                                    <div style="width:${percent}%; background:#007bff; height:20px; border-radius:4px; display:flex; align-items:center; justify-content:center; color:white; font-size:12px; font-weight:bold;">${percent}%</div>
                                                </div>`;
                                            }
                                        }
                                        return `<div class="loading" style="margin:4px 0;">${msg}</div>`;
                                    }).join('');
                                    statusDiv.innerHTML = progressBar + progressMsgs;
                                }
                            };

                            eventSource.onerror = (error) => {
                                statusDiv.innerHTML = `<p class="error">Connection error during initialization</p>`;
                                eventSource.close();
                            };
                        } catch (error) {
                            statusDiv.innerHTML = `<p class="error">Failed to initialize: ${error}</p>`;
                        }
                    }

                    async function executeComparison() {
                        const query = document.getElementById('queryInput').value;
                        if (!query) {
                            alert('Please enter a query');
                            return;
                        }

                        const statusDiv = document.getElementById('queryStatus');
                        statusDiv.innerHTML = '<p class="loading">Executing comparison...</p>';

                        try {
                            const response = await fetch('/api/compare', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ session_id: currentSessionId, query: query })
                            });

                            const result = await response.json();

                            if (response.ok) {
                                displayResults(result);
                                statusDiv.innerHTML = '<p class="status">✓ Comparison complete</p>';
                                loadSummary();
                            } else {
                                statusDiv.innerHTML = `<p class="error">Error: ${result.error}</p>`;
                            }
                        } catch (error) {
                            statusDiv.innerHTML = `<p class="error">Failed to execute: ${error}</p>`;
                        }
                    }

                    function displayResults(result) {
                        const standard = result.systems.standard_rag;
                        const pageindex = result.systems.pageindex_rag;

                        let standardHTML = '';
                        if (standard.status === 'success') {
                            standardHTML = `
                                <div class="result">
                                    <p><strong>Response:</strong></p>
                                    <p>${standard.response}</p>
                                    <div class="metadata">
                                        <p>Execution Time: ${standard.execution_time_seconds.toFixed(2)}s</p>
                                        <p>Chunks Retrieved: ${standard.num_chunks_retrieved}</p>
                                        <p>Approach: Vector Similarity Search</p>
                                    </div>
                                </div>
                            `;
                        } else {
                            standardHTML = `<p class="error">Error: ${standard.error}</p>`;
                        }

                        let pageindexHTML = '';
                        if (pageindex.status === 'success') {
                            const sectionsStr = pageindex.retrieved_sections ? 
                                pageindex.retrieved_sections.join(', ') : 'N/A';
                            pageindexHTML = `
                                <div class="result">
                                    <p><strong>Response:</strong></p>
                                    <p>${pageindex.response}</p>
                                    <div class="metadata">
                                        <p>Execution Time: ${pageindex.execution_time_seconds.toFixed(2)}s</p>
                                        <p>Sections Retrieved: ${pageindex.num_sections_retrieved}</p>
                                        <p>Approach: Tree Search + Reasoning</p>
                                        <p><strong>Reasoning:</strong> ${pageindex.reasoning}</p>
                                        <p><strong>Sections:</strong> ${sectionsStr}</p>
                                    </div>
                                </div>
                            `;
                        } else {
                            pageindexHTML = `<p class="error">Error: ${pageindex.error}</p>`;
                        }

                        document.getElementById('standardResult').innerHTML = standardHTML;
                        document.getElementById('pageindexResult').innerHTML = pageindexHTML;
                    }

                    async function loadSummary() {
                        try {
                            const response = await fetch(`/api/summary/${currentSessionId}`);
                            const summary = await response.json();
                            document.getElementById('summary').innerHTML = `<pre>${JSON.stringify(summary, null, 2)}</pre>`;
                        } catch (error) {
                            console.error('Failed to load summary:', error);
                        }
                    }

                    // Initialize
                    loadPDFs();
                </script>
            </body>
            </html>
            """
            return html

        def run(self, host="127.0.0.1", port=5000, debug=False):
            """Run the Flask web server."""
            print(f"\nStarting web interface at http://{host}:{port}")
            self.app.run(host=host, port=port, debug=debug)


async def main():
    """Main entry point for comparison tool."""
    import argparse

    parser = argparse.ArgumentParser(description="RAG Comparison Tool")
    parser.add_argument(
        "--mode",
        choices=["cli", "web"],
        default="cli",
        help="Running mode (default: cli)"
    )
    parser.add_argument("--port", type=int, default=5000, help="Web server port")

    args = parser.parse_args()

    if args.mode == "web":
        if not HAS_FLASK:
            print("Flask is required for web mode. Install with: pip install flask")
            sys.exit(1)
        web = WebComparator()
        web.run(port=args.port)
    else:
        await CLIComparator.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
