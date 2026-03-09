# RAG Comparison Scoring Sheet

Use this to record and compare results as you test questions.

---

## Quick Score Card

Keep track as you ask questions. Higher scores = better performance.

### 🟢 Warm-up Questions (Q1-3)

| # | Question | Standard RAG Score | PageIndex RAG Score | Winner | Notes |
|---|----------|------|------|--------|-------|
| Q1 | Four vulnerabilities | __/100 | __/100 | __ | Both should be near-perfect |
| Q2 | BTFP end date | __/100 | __/100 | __ | Factual - no reasoning needed |
| Q3 | Stablecoin size | __/100 | __/100 | __ | Numerical data lookup |
| **AVG** | | __/100 | __/100 | **Tie** | Expected: ~95/100 both |

---

### 🟡 Advantage Round (Q4-6)

| # | Question | Standard RAG | PageIndex RAG | Winner | Key Difference |
|---|----------|------|------|--------|-------|
| Q4 | Shocks vs Vulnerabilities | Accuracy: __/100 Completeness: __/100 | Accuracy: __/100 Completeness: __/100 | __ | PageIndex should show clearer semantic understanding |
| Q5 | What makes funding risk unique? | Accuracy: __/100 Reasoning: __/100 | Accuracy: __/100 Reasoning: __/100 | __ | Watch for explicit explanation of structure |
| Q6 | Why overvalued assets risky? | Accuracy: __/100 Completeness: __/100 | Accuracy: __/100 Completeness: __/100 | __ | PageIndex should cover all causal factors |
| **AVG** | | __/100 | __/100 | **PageIndex by ~10%** | Advantage pages emerging |

---

### 🔴 Critical Distinction Round (Q7-10)

| # | Question | Standard RAG | PageIndex RAG | Winner | Margin |
|---|----------|------|------|--------|-------|
| Q7 | SVB + Multi-vulnerabilities | Accuracy: __/100 Completeness: __/100 Reasoning: __/100 | Accuracy: __/100 Completeness: __/100 Reasoning: __/100 | __ | **Expected PageIndex +25%** |
| Q8 | Debt decline vs service ability | Accuracy: __/100 Completeness: __/100 | Accuracy: __/100 Completeness: __/100 | __ | **Expected PageIndex +30%** |
| Q9 | Compare institutions leverage | Accuracy: __/100 Completeness: __/100 Structure: __/100 | Accuracy: __/100 Completeness: __/100 Structure: __/100 | __ | **Expected PageIndex +35%** |
| Q10 | System feedback loops | Accuracy: __/100 Logic clarity: __/100 | Accuracy: __/100 Logic clarity: __/100 | __ | **Expected PageIndex +40%** |
| **AVG** | | __/100 | __/100 | **PageIndex by 33%** | Clear winner emerges |

---

### 🟣 Excellence Round (Q11-15)

| # | Question | Standard RAG | PageIndex RAG | Winner | Margin |
|---|----------|------|------|--------|-------|
| Q11 | Credit quality ÷ default contradiction | Accuracy: __/100 Nuance: __/100 | Accuracy: __/100 Nuance: __/100 | __ | **Expected PageIndex +35%** |
| Q12 | Risk sectors in strong economy | Accuracy: __/100 Identification: __/100 Justification: __/100 | Accuracy: __/100 Identification: __/100 Justification: __/100 | __ | **Expected PageIndex +40%** |
| Q13 | Strategic emphasis of BTFP | Accuracy: __/100 Strategic insight: __/100 | Accuracy: __/100 Strategic insight: __/100 | __ | **Expected PageIndex +45%** |
| Q14 | Document strategy question | Accuracy: __/100 Inference: __/100 | Accuracy: __/100 Inference: __/100 | __ | **Expected PageIndex +50%** |
| Q15 | Missing information inference | Accuracy: __/100 Inference: __/100 | Accuracy: __/100 Inference: __/100 | __ | **Expected PageIndex +45%** |
| **AVG** | | __/100 | __/100 | **PageIndex by 43%** | PageIndex dominates |

---

## Overall Comparison Summary

```
Question Category          Standard RAG    PageIndex RAG    Difference
─────────────────────────────────────────────────────────────────
🟢 Warm-up (Q1-3)             __/100          __/100        __/100
🟡 Advantage (Q4-6)           __/100          __/100        __/100
🔴 Critical (Q7-10)           __/100          __/100        __/100  ← Key difference emerges here
🟣 Excellence (Q11-15)        __/100          __/100        __/100  ← PageIndex dominates here

OVERALL AVERAGE:              __/100          __/100        __/100

VERDICT: 
□ Standard RAG Better (unlikely)
□ Roughly Tied in Performance (only if Q1-3 dominate)
✓ PageIndex Better (expected given question design)
```

---

## Quick Visual Indicator

Print this and mark as you test:

```
Performance by Category:

Warm-up:      S |████████| P   (Expected: Tie)
              
Advantage:    S |██████  |     (Expected: PageIndex ahead)
              P |████████|

Critical:     S |████    |     (Expected: PageIndex clear winner)
              P |████████|

Excellence:   S |██      |     (Expected: PageIndex dominant)
              P |████████|


Legend: S = Standard RAG, P = PageIndex RAG
```

---

## Detailed Scoring Notes

For each category, record:

### If Testing Q7 (SVB Multi-Vulnerability):

**Standard RAG Response Quality:**
- Does it mention SVB explicitly? Y/N
- Does it connect to fair value losses? Y/N  
- Does it mention funding fragility? Y/N
- Does it mention bank runs? Y/N
- Does it explain the systemic risk exception? Y/N
- Does it mention BTFP? Y/N
- Total connections made: __/6

**PageIndex RAG Response Quality:**
- Does it mention Asset Valuation section? Y/N
- Does it mention Funding Risk section? Y/N
- Does it explain the feedback loop? Y/N
- Does it mention why contagion was a concern? Y/N
- Does it explain why policy tools worked? Y/N
- Does it show the reasoning path ("First I checked X section...")? Y/N
- Total connections made: __/6
- **Explicit reasoning shown?** Y/N ← This is the key differentiator

---

### If Testing Q8 (Debt vs Service Ability):

**Standard RAG:**
- Retrieved debt decline information? Y/N
- Retrieved interest coverage information? Y/N
- Explained why both are true? Y/N
- Mentioned GDP growth context? Y/N
- **Clarity:** Low / Medium / High

**PageIndex RAG:**
- Navigated to credit-to-GDP ratio section? Y/N
- Navigated to interest coverage ratio section? Y/N
- Explained they measure different things? Y/N
- Mentioned nominal GDP growth context? Y/N
- Showed reasoning about why both true? Y/N
- **Clarity:** Low / Medium / High

**Key Difference Expected:**
- Standard RAG: Lists facts separately
- PageIndex RAG: Explains relationship between facts

---

### If Testing Q14 (Document Strategy):

**Standard RAG Response to "What's the implicit message?":**
- Can it infer from document structure? Y/N
- Does answer go beyond explicit text? Y/N
- Quality rating: Poor / Fair / Good / Excellent

**PageIndex RAG Response to "What's the implicit message?":**
- Does it identify monitoring emphasis? Y/N
- Does it note quarterly assessment? Y/N
- Does it mention tool/policy implications? Y/N
- Does it reference document structure/organization? Y/N
- Quality rating: Poor / Fair / Good / Excellent

**Expected Result:** PageIndex should be "Good-Excellent"; Standard RAG "Fair-Good"

---

## Expected Benchmark Scores

If you want to know if results align with expectations:

### Warm-up Round (Q1-3)
**Expected Benchmark:**
- Standard RAG: 92/100
- PageIndex RAG: 93/100
- Difference: -1/100 (essentially tied)

### Advantage Round (Q4-6)
**Expected Benchmark:**
- Standard RAG: 78/100
- PageIndex RAG: 88/100
- Difference: +10/100 (PageIndex ahead)

### Critical Round (Q7-10)
**Expected Benchmark:**
- Standard RAG: 65/100
- PageIndex RAG: 85/100
- Difference: +20/100 (PageIndex clearly better)

### Excellence Round (Q11-15)
**Expected Benchmark:**
- Standard RAG: 48/100
- PageIndex RAG: 80/100
- Difference: +32/100 (PageIndex dominates)

**Overall Average:**
- Standard RAG: 71/100
- PageIndex RAG: 87/100
- **PageIndex Advantage: 16 percentage points**

---

## Decision Tree: What Results Mean

```
Your Results:

Is PageIndex score > Standard RAG score in Excellence round (Q11-15)?
├─ Yes: ✓ PageIndex superiority DEMONSTRATED
│       └─ Margin > 25 points? → STRONG evidence
│       └─ Margin 10-25 points? → MODERATE evidence
│       └─ Margin < 10 points? → WEAK evidence
│
└─ No: ✗ Results unexpected
       └─ Check if both systems answers actually differ
       └─ Verify Standard RAG fully retrieved all chunks
       └─ Verify PageIndex reasoning is explicit
```

---

## Final Determination

After completing all 15 questions:

**PageIndex RAG is demonstrably better IF:**
- ✓ Warm-up round shows ~equal performance (both right around 90+)
- ✓ Advantage round shows PageIndex ahead (10+ point gap)
- ✓ Critical round shows clear PageIndex win (25+ point gap)
- ✓ Excellence round shows PageIndex dominates (30+ point gap)

**Conclusion Strength:**
| Pattern | Conclusion |
|---------|-----------|
| All gaps present as expected | **STRONG: PageIndex is clearly superior for complex reasoning** |
| Most gaps present (missing 1) | **MODERATE: PageIndex advantage evident** |
| Some gaps present (missing 2+) | **WEAK: Consider whether questions match document** |
| No gaps present | **UNLIKELY: Recheck both systems for proper functionality** |

---

## Documentation

Save this completed scoresheet and the JSON exports from the comparison tool:
- Timestamp: ________________
- PDF Used: Federal Reserve 2023 Annual Report
- Total Questions Asked: __/15
- Date Completed: ________________
- Evaluator: ________________

**Recommendation:** Store results in `comparison_results_[date].json` and this scoresheet for future reference and demo purposes.
