# How to Use the RAG Comparison Tool

## Overview

The **RAG Comparison Tool** allows you to compare the performance and behavior of two different Retrieval-Augmented Generation (RAG) systems on your PDF documents:

- **Standard RAG**: Traditional vector-based RAG using semantic similarity search, chunking, and embeddings
- **PageIndex RAG**: Vectorless, reasoning-based RAG using document structure and LLM reasoning for retrieval

This tool helps you understand the differences in retrieval accuracy, execution time, and response quality between the two approaches on professional documents.

## Why Compare?

- **Vector Search Limitations**: Traditional vector-based RAG relies on semantic similarity, which doesn't always equal relevance for complex documents
- **Human-like Retrieval**: PageIndex simulates how human experts navigate documents through tree-based reasoning
- **No Chunking Artifacts**: PageIndex preserves natural document structure instead of splitting text into arbitrary chunks
- **Better Interpretability**: Reasoning-based retrieval provides traceable, explainable results

## Prerequisites

### Requirements
- Python 3.8+
- OpenAI API key (for both RAG systems)
- PDF files to test (place in `tests/pdfs/` directory)

### Dependencies
The following packages are required (included in `requirements.txt`):
- `openai==1.101.0` - OpenAI API client
- `pymupdf==1.26.4` - PDF processing
- `sentence-transformers==2.2.2` - For Standard RAG embeddings
- `faiss-cpu==1.7.4` - Vector similarity search
- `flask` (optional) - For web interface
- `tiktoken==0.11.0` - Token counting

## Setup Steps

### Step 1: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# For web interface (optional)
pip install flask
```

### Step 2: Configure OpenAI API Key

The tool uses your OpenAI API key. Set it up in one of these ways:

**Option A: Environment Variable**
```bash
# On Windows (PowerShell):
$env:OPENAI_API_KEY="your-api-key-here"

# On Windows (Command Prompt):
set OPENAI_API_KEY=your-api-key-here

# On macOS/Linux:
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: .env File**
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

### Step 3: Prepare Test PDFs

1. Create a `tests/pdfs/` directory if it doesn't exist:
   ```bash
   mkdir -p tests/pdfs
   ```

2. Add your PDF files to this directory:
   ```bash
   cp /path/to/your/document.pdf tests/pdfs/
   ```

3. Supported formats: Any PDF file (recommended 10+ pages for meaningful comparison)

### Step 4: Verify Setup

Test your setup by listing available PDFs:
```python
from pageindex.comparison_ui import CLIComparator
import asyncio

pdfs = CLIComparator.get_available_pdfs()
print(f"Found {len(pdfs)} PDF files:")
for pdf in pdfs:
    print(f"  - {pdf}")
```

## How PageIndex RAG Works

### Tree Search Process

PageIndex RAG performs intelligent retrieval in two steps:

1. **Structure Analysis**: The document is automatically parsed into a hierarchical tree structure where:
   - Each node represents a section or subsection
   - Each node contains a title, summary, and page numbers
   - The hierarchy preserves the document's natural organization

2. **Reasoning-Based Retrieval**: When you ask a query:
   - The LLM performs tree search using explicit reasoning
   - It evaluates which sections are relevant based on understanding, not just keywords
   - It selects top-5 most relevant sections
   - It explains why each section was selected

3. **Answer Generation**: From the retrieved sections:
   - Context is compiled from summaries and metadata
   - GPT-4o generates a comprehensive answer
   - The answer includes references to which sections provided the information

### Why This Matters

**Vector Similarity Limitations:**
- Vector similarity measures how "close" embeddings are, not true relevance
- "Relevant" and "similar" are not the same thing
- Professional documents need semantic understanding, not vibe retrieval

**PageIndex's Advantages:**
- Reasoning-based retrieval preserves semantic meaning
- Explicit reasoning makes retrieval decisions transparent and traceable
- Hierarchical structure reduces noise from unrelated similar content
- Human-like navigation through document structure
- Better at disambiguating between similar-looking but different concepts
- Scales better to long documents (structure-based vs vector-based)

## Usage Modes

### Mode 1: Command-Line Interactive (CLI)

**Start the interactive comparison tool:**

```bash
python pageindex/comparison_ui.py --mode cli
```

**Example Session:**

```
============================================================
RAG COMPARISON TOOL - Interactive Mode
============================================================

Available PDFs:
  1. 2023-annual-report.pdf
  2. financial-summary.pdf

Select a PDF (number): 1

Initializing RAG systems for 2023-annual-report.pdf...
Setting up Standard RAG...
Setting up PageIndex RAG...

============================================================
Ready to compare. Enter queries or type 'quit' to exit.
============================================================

Query: What were the revenue figures for Q3?

Executing queries on both systems...

------------------------------------------------------------
COMPARISON RESULTS
------------------------------------------------------------

Standard RAG Response:
  Time: 2.34s
  Chunks Retrieved: 3
  Answer: The Q3 revenue was $2.4 billion, representing a 5% increase...

PageIndex RAG:
  Document Structure: structure_available

============================================================
COMPARISON SUMMARY
============================================================
{
  "pdf": "2023-annual-report.pdf",
  "total_queries": 1,
  "standard_rag": {
    "avg_execution_time": 2.34,
    "avg_chunks_retrieved": 3,
    "success_rate": 1.0
  },
  "pageindex_rag": {
    "structure_size": 45,
    "status": "available"
  }
}

Results saved to comparison_results_2023-annual-report.json
```

**Features:**
- Select from available PDFs in `tests/pdfs/`
- Enter queries interactively and see responses from both systems
- View execution time, chunks retrieved, and token usage
- Results automatically saved as JSON for analysis

### Mode 2: Web Interface

**Start the web server:**

```bash
python pageindex/comparison_ui.py --mode web --port 5000
```

**Access the interface:**
- Open your browser and navigate to: `http://127.0.0.1:5000`
- Or use a different port: `http://127.0.0.1:YOUR_PORT`

**Web Interface Features:**

1. **PDF Selection Panel**
   - Dropdown menu showing all available PDFs from `tests/pdfs/`
   - "Initialize RAG Systems" button to load and prepare systems

2. **Query Panel** (appears after initialization)
   - Text area for entering your questions
   - "Compare Systems" button to execute the comparison
   - Status messages for initialization and execution

3. **Results Display** (split view)
   - **Standard RAG**: Shows response text, execution time, chunks retrieved
   - **PageIndex RAG**: Shows document structure status and information

4. **Summary Statistics**
   - Average execution time across all queries
   - Chunk retrieval statistics
   - Success rates
   - Document structure metrics

## Understanding the Results

### What's Being Compared

Both RAG systems now answer your queries and can be directly compared:

**Standard RAG:**
- Uses vector embeddings to find semantically similar text chunks
- Retrieves fixed-size chunks (512 characters with 100-character overlap)
- Generates answer from the retrieved chunks using GPT-4o

**PageIndex RAG:**
- Uses LLM reasoning to navigate the document hierarchy tree
- Identifies relevant sections based on semantic understanding of structure
- Generates answer from the selected sections with explicit reasoning
- Shows which sections were selected and why

### Standard RAG Metrics

| Metric | Meaning |
|--------|---------|
| **Execution Time** | How long the query took to process (in seconds) |
| **Chunks Retrieved** | Number of text chunks extracted from the PDF |
| **Response** | The generated answer to your question |
| **Status** | "success" if query executed without errors |
| **Tokens Used** | Rough estimate of tokens consumed |

### PageIndex RAG Metrics

| Metric | Meaning |
|--------|---------|
| **Execution Time** | Time taken for tree search + answer generation (in seconds) |
| **Sections Retrieved** | Number of document sections identified as relevant |
| **Response** | The generated answer based on retrieved sections |
| **Reasoning** | Explanation of why these sections were selected |
| **Retrieved Sections** | Names/titles of the sections used for answering |
| **Status** | "success" if retrieval and generation succeeded |

### Comparison Interpretation

**When Standard RAG excels:**
- Simple, straightforward queries with direct answers
- When query keywords closely match document text
- Quick response times for vector similarity (but may miss context)
- Works well with small, flat documents

**When PageIndex RAG excels:**
- Complex, multi-step questions requiring domain reasoning
- Long professional documents with clear hierarchical structure
- Queries requiring understanding across multiple sections
- When you need transparent, explainable retrieval decisions
- Better at preserving context and section relationships
- Demonstrated 98.7% accuracy on FinanceBench (vs lower for vector-based)

## Output Files

### JSON Results Format

When you exit the CLI tool, results are saved as `comparison_results_<pdf_name>.json`:

```json
{
  "pdf": "2023-annual-report.pdf",
  "comparison_results": [
    {
      "query": "What were the revenue figures for Q3?",
      "timestamp": 1234567890.123,
      "systems": {
        "standard_rag": {
          "response": "The Q3 revenue was...",
          "retrieved_chunks": [...],
          "num_chunks_retrieved": 3,
          "tokens_used": 125,
          "execution_time_seconds": 2.34,
          "status": "success"
        },
        "pageindex_rag": {
          "structure": {...},
          "note": "PageIndex RAG returns document structure...",
          "status": "structure_available"
        }
      }
    }
  ],
  "summary": {
    "pdf": "2023-annual-report.pdf",
    "total_queries": 1,
    "standard_rag": {...},
    "pageindex_rag": {...}
  }
}
```

## Advanced Configuration

### Configuring RAG Systems

You can customize the RAG systems by editing the `RAGComparator` class in `pageindex/comparison_ui.py`:

**Standard RAG Configuration:**
```python
self.standard_rag = StandardRAG(
    model_name="gpt-4o-2024-11-20",  # Change model
    chunk_size=512,                   # Size of text chunks
    chunk_overlap=100,                # Overlap between chunks
    top_k=3                           # Number of chunks to retrieve
)
```

**PageIndex RAG Configuration:**
```python
# Edit options in page_index_main() call:
opt = config(
    model="gpt-4o-2024-11-20",
    toc_check_page_num=20,
    max_page_num_each_node=10,
    max_token_num_each_node=20000,
    if_add_node_summary='yes'
)
```

## Troubleshooting

### Issue: "No PDF files found in tests/pdfs/"

**Solution:**
1. Ensure `tests/pdfs/` directory exists
2. Add PDF files to this directory
3. Verify file extensions are `.pdf` (lowercase)

### Issue: "OPENAI_API_KEY not found"

**Solution:**
1. Set the environment variable (see Setup Step 2)
2. Verify it's set: `echo $OPENAI_API_KEY` (macOS/Linux) or `echo $env:OPENAI_API_KEY` (Windows)
3. Or create a `.env` file in the project root

### Issue: "Flask is required for web mode"

**Solution:**
```bash
pip install flask
```

### Issue: "PDF processing errors" or "Timeout"

**Solution:**
1. Try a smaller PDF file first to test the setup
2. Check PDF file integrity
3. Increase CloudFile timeout settings if using large documents

### Issue: Web interface shows "Initializing..." but doesn't complete

**Solution:**
1. Check browser console for JavaScript errors (F12 → Console)
2. Ensure OpenAI API key is correctly set
3. Check terminal output for error messages
4. Try CLI mode to isolate the issue

## Example Workflows

### Workflow 1: Quick Comparison on a Document

```bash
# 1. Start CLI mode
python pageindex/comparison_ui.py --mode cli

# 2. Select your PDF from the list
# 3. Ask 3-5 test questions
# 4. Review the automatically saved results JSON
```

### Workflow 2: Systematic Performance Testing

```bash
# 1. Prepare multiple PDFs in tests/pdfs/
# 2. Start with CLI mode and multiple test questions
# 3. Save results for each document
# 4. Analyze JSON outputs to compare metrics
```

### Workflow 3: Interactive Web-Based Exploration

```bash
# 1. Start web server: python pageindex/comparison_ui.py --mode web
# 2. Open browser: http://127.0.0.1:5000
# 3. Initialize RAG systems for your PDF
# 4. Ask exploratory questions
# 5. View results side-by-side in real-time
```

## Performance Tips

1. **Start Small**: Test with 10-20 page documents first
2. **Use Same Questions**: Compare both systems on identical queries
3. **Check Internet**: Ensure stable connection to OpenAI API
4. **Token Budgets**: Monitor API usage and token consumption
5. **Document Quality**: High-quality PDFs with clear structure yield better results

## Next Steps

- Review the [PageIndex Framework Blog Post](https://pageindex.ai/blog/pageindex-intro) for theoretical background
- Check [Vectorless RAG Cookbook](https://docs.pageindex.ai/cookbook/vectorless-rag-pageindex) for more examples
- Explore [Vision-based RAG](https://docs.pageindex.ai/cookbook/vision-rag-pageindex) for OCR-free document processing
- Visit [PageIndex Documentation](https://docs.pageindex.ai) for comprehensive guides

## Support

For issues and questions:
- Check existing [GitHub Issues](https://github.com/VectifyAI/PageIndex/issues)
- Ask in the [Discord Community](https://discord.com/invite/VuXuf29EUj)
- Visit the official [documentation](https://docs.pageindex.ai)
