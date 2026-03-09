# Best Questions to Demonstrate PageIndex RAG Superiority

## Document Analysis

**Source:** Federal Reserve 2023 Annual Report (Financial Stability Section)

**Key Characteristics:**
- Highly hierarchical structure (Sections → Subsections → Topics)
- Complex interconnections between concepts
- Multiple perspectives on related topics
- Technical financial terminology
- Time-series data and trend analysis
- Cross-references between sections

## Why This Document Reveals PageIndex's Advantage

### Standard RAG Limitations on This Content:
- **Keyword matching fails**: Many sections use similar financial terms
- **Chunk fragmentation**: Splitting on "Leverage" will get wrong context
- **Lost relationships**: Can't connect concepts across sections (SVB crisis → funding risk → bank runs)
- **Hierarchy ignored**: Treats all information equally regardless of structure
- **Ambiguity**: "Leverage in the Financial System" vs "Gross leverage of large businesses" both match

### PageIndex RAG Advantages:
- **Structure-aware**: Understands document hierarchy
- **Reasoning-based**: Evaluates semantic relevance, not keyword similarity
- **Relationship-aware**: Connects related concepts across sections
- **Context-preserved**: Maintains section hierarchy and relationships

---

## Question Categories (Ordered by Difficulty)

### ☆ Category 1: Simple Direct Lookup (Both RAG Systems Succeed)

These questions have straightforward answers in specific sections. Both systems should answer correctly.

**Purpose:** Establish baseline accuracy

#### Questions:
1. "What are the four key vulnerabilities monitored by the Federal Reserve?"
   - Answer location: Page with Figure 3.1
   - Expected: Asset valuation, Funding risk, Borrowing, Leverage in financial sector

2. "When did the Bank Term Funding Program (BTFP) end?"
   - Answer location: Funding Risk section
   - Expected: March 11, 2024

3. "What is stablecoin assets around?"
   - Answer location: Funding Risk section
   - Expected: Around $125 billion

**Why both systems succeed:** Clear, specific terminology with exact answers that appear verbatim.

---

### ☆☆ Category 2: Concept Definition and Explanation (PageIndex Advantage)

These require understanding a concept across its definition, examples, and implications within the document structure.

**Purpose:** Show PageIndex's ability to understand concepts holistically

#### Questions:
1. "Explain the difference between 'shocks' and 'vulnerabilities' in financial stability?"
   - Standard RAG challenge: Both terms appear in multiple sections; keyword matching may retrieve wrong definitions
   - PageIndex advantage: Navigates to definition section first, understands conceptual relationship
   - Expected answer: Shocks are unpredictable events; vulnerabilities build over time and cause problems under stress

2. "Why would high asset valuations become a vulnerability?"
   - Standard RAG challenge: Answer scattered across sections with multiple examples (equities, real estate, farmland)
   - PageIndex advantage: Understands hierarchical structure of "Asset Valuation Pressures" section
   - Expected answer: Because unwinding of high prices can be destabilizing, especially with leverage involved

3. "What makes funding risk different from other financial vulnerabilities?"
   - Standard RAG challenge: Must distinguish among four similar-length vulnerability sections
   - PageIndex advantage: Tree structure makes section relationships clear
   - Expected answer: Funding risk specifically exposes to "runs" - rapid withdrawal of funds

4. "How does the Federal Reserve define a 'stable' financial system?"
   - Standard RAG challenge: Definition embedded in introduction paragraph, not labeled as definition
   - PageIndex advantage: Understands opening section defines system capability during shocks
   - Expected answer: Ability to continue meeting demands for financial services when hit by adverse events

---

### ☆☆☆ Category 3: Multi-Step Reasoning (PageIndex Major Advantage)

Questions requiring combining information from multiple sections to reach a conclusion.

**Purpose:** Demonstrate PageIndex's hierarchical reasoning advantage

#### Questions:
1. "How did SVB's problems relate to the four key vulnerabilities the Federal Reserve monitors?"
   - Standard RAG challenge: 
     - SVB mentioned only in "Leverage in Financial System" section
     - Need to connect to all four monitoring areas
     - Chunks won't have enough context for relationship explanation
   - PageIndex advantage: 
     - Navigates to multiple sections systematically
     - Understands hierarchical relationship between SVB example and vulnerability framework
   - Expected answer: SVB failed due to fair value losses (Asset Valuation) + fragile funding structures (Funding Risk) + leverage interaction + bank runs showing interconnection

2. "What is the relationship between household debt, business borrowing, and financial institution health?"
   - Standard RAG challenge: 
     - Requires three separate sections: "Borrowing by Households and Businesses," "Leverage in Financial System," and bank-specific content
     - Would need multiple chunk retrievals to synthesize
   - PageIndex advantage: 
     - Hierarchical structure shows all under Financial Stability monitoring
     - Understands feedback loop: households → financial institutions → system stability
   - Expected answer: Complex feedback loop where household/business debt affects institution health, institution health affects credit availability, creating cascading effects

3. "What changed in 2023 that reduced systemic risk from non-bank financing?"
   - Standard RAG challenge: 
     - Answer spans: private credit growth, money market fund reforms, stablecoin discussion
     - Hard to connect without structure
   - PageIndex advantage: 
     - Understands where "changes" appear in document sections
     - Identifies Money Market Fund rule changes by SEC as key reform
     - Finds Bank Term Funding Program end date
     - Connects to Private Credit Funds growth being monitored
   - Expected answer: SEC rule changes for MMFs in July 2023, BTFP ended March 2024, but new risks (stablecoins, private credit opacity) remain

4. "Compare leverage levels across different types of financial institutions"
   - Standard RAG challenge: 
     - Information scattered: banks vs life insurance vs hedge funds
     - Each requires different context
     - Chunks won't capture comparative framework
   - PageIndex advantage: 
     - Hierarchical "Leverage in Financial System" section subsumes all
     - Can navigate and compare systematically
   - Expected answer: Banks (CET1 ratios near high), insurance (middle of historical range), hedge funds (elevated and stabilized)

---

### ☆☆☆☆ Category 4: Contradiction Resolution (PageIndex Excellence)

Questions where different sections appear to say different things, requiring nuanced understanding.

**Purpose:** Show where PageIndex's reasoning beats vector similarity

#### Questions:
1. "The report says business debt declined, but also that businesses are well-positioned to service debt. How are both true?"
   - Standard RAG challenge: 
     - These appear in different sections ("Borrowing by..." vs "Leverage in...")
     - Vector similarity might retrieve contradictory chunks
     - Can't resolve without spatial/hierarchical understanding
   - PageIndex advantage: 
     - Understands both statements are in same monitoring context
     - Navigates to understand declining debt (ratio) ≠ ability to manage (interest coverage)
     - Recognizes GDP growth context makes ratio decline significant
   - Expected answer: Credit-to-GDP ratio declined because debt fell faster than nominal GDP grew; separately, interest coverage ratios remain high showing ability to service existing debt

2. "The report mentions both 'solid earnings' for businesses and 'business credit quality declined.' How can both be true?"
   - Standard RAG challenge: 
     - Appears contradictory without hierarchical context
     - Keywords "credit quality" and "earnings" appear in different sections
   - PageIndex advantage: 
     - Understands these are separate measures (flow vs stock)
     - Earnings are strong NOW but downgrades exceeded upgrades (trend)
     - Both in context of monitoring evolution
   - Expected answer: Strong current earnings support debt service, but trend indicators (upgrades vs downgrades) show deteriorating prospects

---

### ☆☆☆☆☆ Category 5: Implicit Information and Strategic Inference (PageIndex Strongest Advantage)

Questions requiring reading between the lines and understanding document strategy.

**Purpose:** Demonstrates human-level reasoning capability

#### Questions:
1. "What specific financial sectors or institutions is the Federal Reserve most concerned about heading into 2024?"
   - Standard RAG challenge: 
     - No explicit list in document
     - Would retrieve all mentions of concerns equally
     - Can't prioritize by document emphasis or structure
   - PageIndex advantage: 
     - Understands hierarchy shows what gets detailed monitoring
     - Identifies opacity/uncertainty language (hedge funds, private credit, stablecoins)
     - Notes specific mentions of "challenges" for smaller banks
     - Recognizes stress language around CRE lending
   - Expected answer: Hedge funds (opacity, Treasury basis trade growth), Private credit (rapid growth, opacity), Stablecoins (lack of oversight), smaller banks with CRE exposure, life insurance companies (risky asset allocation)

2. "Why did the Federal Reserve emphasize the BTFP and systemic risk exception in discussing SVB?"
   - Standard RAG challenge: 
     - Factual details available, but not the strategic "why emphasize"
     - Vector retrieval won't understand document framing
   - PageIndex advantage: 
     - Understands placement: comes after disaster description
     - Recognizes emphasis on "mitigated" and "stopped contagion"
     - Connects to financial stability monitoring framework
   - Expected answer: Demonstrates Fed's toolkit was effective in managing acute crisis, preventing broader contagion, and stabilizing system—important for public confidence and future risk management

3. "What is the Federal Reserve's implicit message about the relationship between structure and stability?"
   - Standard RAG challenge: 
     - Question has no direct answer anywhere
     - Would retrieve random structural mentions
   - PageIndex advantage: 
     - Understands document structure itself teaches lesson
     - Sees monitoring framework repeated quarterly
     - Notes "shocks vs vulnerabilities" distinction placement at outset
     - Recognizes how section organization (from individual institutions to system) reflects understanding
   - Expected answer: System resilience depends on understanding complex linkages and monitoring vulnerabilities over time; structure matters because vulnerabilities build gradually but create cascading effects

4. "Which financial stability risks mentioned in the report are most difficult to monitor and why?"
   - Standard RAG challenge: 
     - Answer requires implicit understanding
     - "Difficult" not explicitly stated
   - PageIndex advantage: 
     - Recognizes opacity language: "opaque" (private credit), "fragile" (stablecoins), "difficult to judge" (asset valuations)
     - Understands hierarchy of measurable vs. difficult risks
     - Connects to international coordination sections showing challenges
   - Expected answer: Asset valuations (hard to judge overvaluation), hedge funds leveraging Treasury markets (opacity), private credit expansion (opaque sector), stablecoins (lack regulatory oversight, crypto spillover risk)

---

## Testing Strategy for Optimal Demonstration

### Phase 1: Warm-up (Ask Q1-3 from Category 1)
- **Purpose:** Both systems should succeed equally
- **User expectation:** Setting baseline that both work
- **Time investment:** ~5 minutes
- **Demonstrates:** Tool is functional

### Phase 2: Show the Advantage (Ask Q1-2 from Category 2)
- **Purpose:** Category 2 questions start showing PageIndex strength
- **Comparison focus:** 
  - **Standard RAG:** May retrieve right content but not synthesize the concept
  - **PageIndex RAG:** Shows clear reasoning about concept hierarchy
- **Time investment:** ~10 minutes
- **Demonstrates:** PageIndex better at concept understanding

### Phase 3: Make the Case (Ask Q1-2 from Category 3)
- **Purpose:** Multi-step reasoning is PageIndex's sweet spot
- **Comparison focus:**
  - **Standard RAG:** Gets pieces but struggles to connect across sections
  - **PageIndex RAG:** Shows explicit reasoning paths across sections
- **Time investment:** ~15 minutes
- **User reaction point:** Most users see clear winner here
- **Demonstrates:** PageIndex understands document structure

### Phase 4: Seal It (Ask Q1-2 from Category 4-5)
- **Purpose:** Show PageIndex handles nuance human-like reasoning
- **Comparison focus:**
  - **Standard RAG:** May miss nuance, offer contradictory snippets
  - **PageIndex RAG:** Synthesizes apparent contradictions into coherent explanation
- **Time investment:** ~10 minutes
- **Demonstrates:** PageIndex has true comprehension, not just retrieval

---

## Expected Accuracy Comparison

Based on document characteristics:

| Category | Standard RAG | PageIndex RAG | Winner | Margin |
|----------|-------------|---------------|--------|--------|
| **Simple Lookup** | 90-95% | 90-95% | Tie | ±0% |
| **Concept Definition** | 70-80% | 85-95% | PageIndex | +15% |
| **Multi-Step Reasoning** | 60-75% | 85-95% | PageIndex | +20% |
| **Contradiction Resolution** | 40-60% | 80-90% | PageIndex | +35% |
| **Implicit Information** | 20-40% | 75-85% | PageIndex | +50% |

---

## Questions That Will Make Standard RAG Fail

These are the questions that will clearly show Standard RAG struggling:

1. **Section Name Mismatch:** 
   - "Explain what 'fair value losses' have to do with bank funding risk"
   - Standard RAG would retrieve both separately; PageIndex connects them in Bank Resilience context

2. **Acronym Ambiguity:**
   - "What is BTFP and why was it important?"
   - Standard RAG might get definition wrong or miss temporal context
   - PageIndex understands it relates to March 2023 SVB crisis in specific historical section

3. **Implicit Risk:**
   - "Why might residential real estate price increases be concerning even though the economy is strong?"
   - Standard RAG can't connect "stable economy" + "high prices" → "vulnerability"
   - PageIndex understands Asset Valuation Pressures section logic

4. **Federal vs. System Level:**
   - "How does the Federal Reserve's approach to financial stability differ from individual bank oversight?"
   - Standard RAG treats as single lookup question
   - PageIndex understands hierarchical distinction (Fed monitoring, FSOC coordination, FSB participation)

---

## Preparation Checklist

Before initiating comparison test:

- [ ] Both systems have PDF ingested successfully
- [ ] Web UI is responding with properly formatted results
- [ ] JSON export is working for saving results
- [ ] Timer is accurate (critical for comparing execution speed)
- [ ] Have Section titles ready (don't make users search for them)
- [ ] Have follow-up clarification questions ready (for when Standard RAG gives partial answers)
- [ ] Record both full answers AND process reasoning for comparison

---

## Key Metrics to Track

For each question, record:

1. **Accuracy Score** (0-100): How correct is the answer?
2. **Completeness** (0-100): Does it cover all necessary points?
3. **Reasoning Quality** (0-100): Is the logic clear and well-explained?
4. **Execution Time** (seconds): How long did it take?
5. **Retrieved Items**: How many chunks (RAG) or sections (PIR) were used?
6. **User Confidence** (1-5 scale): How confident do you feel in the answer?

**Expected pattern:** 
- Categories 1-2: Metrics similar
- Categories 3-5: PageIndex dominates on Accuracy, Completeness, Reasoning Quality; Times may be similar or PageIndex slightly longer but better quality

---

## Professional Narrative

When showing results, frame it this way:

> "Notice that on simple lookup questions (Category 1), both systems perform equally. This is expected and good—when questions have straightforward answers, vector search works fine.
>
> But start watching what happens with the more complex questions (Categories 3-4). PageIndex doesn't just retrieve chunks; it actively reasons about which sections are relevant and why. You can see its thought process.
>
> And on the implicit reasoning questions (Category 5), PageIndex shows true comprehension—understanding what the document is trying to communicate, not just finding keywords. This is where PageIndex becomes invaluable for professional documents."
