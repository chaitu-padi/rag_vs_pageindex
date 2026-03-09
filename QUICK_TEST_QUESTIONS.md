# Quick Reference: Test Questions for RAG Comparison

Copy and paste these questions directly into the comparison tool.

---

## 🟢 Warm-up Round (Both Systems Should Succeed)

Establish baseline - both RAG systems should get these right.

### Q1: Simple Definition Lookup
```
What are the four key vulnerabilities monitored by the Federal Reserve?
```
**Expected Answer:** Asset valuation, Funding risk, Borrowing by households/businesses, Leverage in financial sector

---

### Q2: Factual Recall
```
When did the Bank Term Funding Program (BTFP) end?
```
**Expected Answer:** March 11, 2024

---

### Q3: Numerical Data
```
What is the approximate size of stablecoin assets mentioned in the report?
```
**Expected Answer:** Around $125 billion

---

## 🟡 Advantage Round (PageIndex Begins to Show Strength)

PageIndex should provide better synthesis and understanding.

### Q4: Concept Explanation
```
Explain why the Federal Reserve distinguishes between "shocks" and "vulnerabilities" in financial stability monitoring.
```
**Expected Answer:** Shocks are unpredictable and hard to prevent; vulnerabilities are aspects that build over time and are more predictable, so the Fed focuses monitoring on building vulnerabilities to prevent crises.

---

### Q5: Context-Based Definition
```
According to the report, what makes funding risk different from other financial vulnerabilities?
```
**Expected Answer:** Funding risk specifically exposes the financial system to the possibility of "runs"—rapid, mass withdrawals of funds from institutions or sectors, like what happened with SVB.

---

### Q6: Multi-Point Explanation
```
Why would overvalued assets be a vulnerability to financial stability?
```
**Expected Answer:** Overvalued assets are risky because unwinding high prices can be destabilizing, especially if those assets are widely held, supported by leverage, involve maturity transformation, or have risk opacity. It also signals broader risk-taking in the market.

---

## 🔴 Critical Distinction Round (PageIndex Major Advantage)

Multi-section reasoning where PageIndex's hierarchical approach excels.

### Q7: Cross-Section Connection
```
How did Silicon Valley Bank's (SVB) failure demonstrate the connection between multiple financial vulnerabilities?
```
**Expected Answer:** SVB's failure showed how fair value losses on assets (Asset Valuation vulnerability) combined with a fragile funding structure (Funding Risk vulnerability) could amplify shocks. The bank runs triggered by these vulnerabilities demonstrated how interconnected risks can cascade, which is why the Fed used systemic risk exception and BTFP to stop contagion.

---

### Q8: Relationship Between Concepts
```
The report mentions that business debt declined in 2023, but also that businesses remain well-positioned to service debt. How can both statements be true?
```
**Expected Answer:** These are measuring different things: (1) The credit-to-GDP ratio declined because total debt fell while nominal GDP grew—showing less relative borrowing; (2) Interest coverage ratios remain high, showing businesses have strong earnings to service their existing debt obligations. Both trends are positive for financial stability.

---

### Q9: Multi-Institution Comparison
```
Compare leverage levels across different types of financial institutions mentioned in the report.
```
**Expected Answer:** Banks: CET1 capital ratios are near or above the top quartile; Life Insurance Companies: leverage near middle of historical range, well below pandemic peak; Hedge Funds: leverage stabilized at elevated levels due to Treasury basis trading. Overall, banks most resilient, hedge funds more concerning.

---

### Q10: System-Level Understanding
```
What is the relationship between household debt levels, business borrowing, and the health of financial institutions according to the report's framework?
```
**Expected Answer:** These create a feedback loop: excessive household and business debt makes them vulnerable to income/asset value shocks → financial stress at households/businesses creates losses for financial institutions → institutions become weaker and pull back credit → which forces more stress on households and businesses → potentially leading to system-wide instability.

---

## 🟣 Excellence Round (PageIndex's True Strength)

Implicit reasoning and strategic understanding that reveals true comprehension.

### Q11: Contradiction Resolution
```
The report says business credit quality declined slightly in 2023, but also that default rates remained low by historical standards. What explains this seeming contradiction?
```
**Expected Answer:** Credit quality is declining (more downgrades than upgrades), showing deteriorating prospects, but the absolute level of defaults remains low because earnings are currently strong. This indicates emerging risks that aren't yet fully manifested in default rates—a leading indicator the Fed is monitoring.

---

### Q12: Implicit Risk Identification
```
Even though the report states the economy remained strong with growth outlook centered on continued growth, what specific financial sectors is the Federal Reserve most concerned about?
```
**Expected Answer:** Private credit funds (rapid growth, high opacity make assessment difficult), hedge funds (elevated leverage with Treasury basis trade concentration), stablecoins (lack of regulatory oversight, potential for runs, crypto spillover risk), and smaller banks exposed to commercial real estate (fair value losses and potential weakening loan performance).

---

### Q13: Strategic Emphasis
```
Why did the Federal Reserve emphasize the use of the systemic risk exception and the Bank Term Funding Program in its discussion of SVB and banking sector resilience?
```
**Expected Answer:** To demonstrate that the Fed has effective tools to manage acute crises and prevent system-wide contagion. The emphasis shows regulatory confidence that enhanced policy tools can mitigate vulnerabilities and stabilize the system—important for restoring confidence and managing future risks.

---

### Q14: Document Strategy Question
```
Based on the structure and emphasis of the report, what is the Federal Reserve's implicit message about managing financial stability?
```
**Expected Answer:** Financial stability requires: (1) Systematic quarterly monitoring of vulnerabilities before they become crises, (2) Understanding complex interconnections between institutions and economic conditions, (3) Forward-looking analysis of how vulnerabilities interact with potential shocks, (4) Flexibility and coordination across regulatory agencies (FSOC) and international partners (FSB), and (5) Willingness to use extraordinary measures when needed.

---

### Q15: Missing Information Inference
```
What financial stability concerns does the report discuss in detail but suggest are still not well-understood or monitored?
```
**Expected Answer:** Private credit funds (noted as "opaque" making assessment difficult), crypto-asset ecosystem's relationship to traditional finance, and the structural vulnerabilities in money market funds (though reforms were mentioned). The level of detail about what's NOT known indicates these are frontier risks requiring more monitoring.

---

## 📊 Testing Sequence Recommendation

1. **Start with Q1-3** (warm-up) - both should succeed equally
2. **Ask Q4-6** (advantage round) - watch for PageIndex better synthesis
3. **Ask Q7-10** (critical round) - clear PageIndex advantage emerges
4. **Ask Q11-15** (excellence round) - PageIndex dominance becomes obvious

**Total Time:** ~45 minutes for complete demonstration

---

## 🎯 What Success Looks Like

### Standard RAG on Category 🔴 Questions (Q7-10):
- ✓ Retrieves relevant text chunks
- ✓ Quotes correctly from document
- ⚠️ May list disconnected points
- ⚠️ Doesn't clearly explain relationships
- ⚠️ May miss the "why" behind the connections
- ⚠️ Could take multiple prompts to fully answer

### PageIndex RAG on Category 🔴 Questions (Q7-10):
- ✓ Identifies relevant sections systematically
- ✓ Shows explicit reasoning about why sections matter
- ✓ Explains relationships between concepts
- ✓ Integrates information from multiple sections coherently
- ✓ Shows reasoning path ("First I looked at Asset Valuation section, then Funding Risk section...")

---

## 💡 Pro Tips

1. **Pay attention to process, not just answer**: With PageIndex, you'll see WHERE it looked and WHY. With Standard RAG, you'll mostly get results.

2. **Note execution times**: Expect PageIndex to be slightly slower (3-4s vs 2-3s) due to reasoning, but the quality improvement is worth it.

3. **Check reasoning quality**: PageIndex should explicitly explain its reasoning; Standard RAG should not (it just retrieves).

4. **Ask follow-ups**: If either system gives incomplete answer, ask "Can you elaborate on..." to see how each handles follow-up reasoning.

5. **Save the results**: Use the JSON export to review full responses later and score accuracy objectively.

---

## 📋 Answer Quality Scoring Template

For each question, rate both systems:

| Question | Metric | Standard RAG | PageIndex RAG | Notes |
|----------|--------|-------------|---------------|-------|
| Q# | Accuracy | __/100 | __/100 | |
| | Completeness | __/100 | __/100 | |
| | Reasoning Quality | __/100 | __/100 | |
| | Time (sec) | ____ | ____ | |

**Scoring Guide:**
- **Accuracy:** How correct is the answer (0=wrong, 100=perfectly correct)
- **Completeness:** Does it answer all parts of the question (0=partial, 100=complete)
- **Reasoning:** Is the logic clear and well-explained (0=none, 100=excellent)

**Expected Pattern:** Categories 1-2 similar scores, Categories 3-5 PageIndex significantly higher.
