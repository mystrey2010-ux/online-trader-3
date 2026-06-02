# Hermes Optimized Session Prompts

---

# Prompt 1 — Bootstrap Prompt

Use at session start.

```text
You are initializing a new session in the current project directory. 
Your first task is to read, internalize, and map the following project files:
docs/ (ARCHITECTURE.md, CHANGELOG.md, DECISIONS.md, KNOWN_ISSUES.md, PROJECT_STATE.md)

Before executing any code or modifications, emit a grounding summary using this exact structure:

<session_bootstrap>
### 1. Current Objective & Focus
[Clear, high-density target for this session]

### 2. System State & Active Architecture
[Concise summary of components active right now]

### 3. Blockers, Risks & Inconsistencies
[Explicit technical friction or conflicting logic identified in docs]

### 4. Recommended Next Actions
- [ ] Action item 1
- [ ] Action item 2
</session_bootstrap>

Critical Execution Rules:
- Do not write, refactor, or propose code changes until this bootstrap is complete.
- Adhere strictly to past architectural invariants and documented decisions.
- Reject previously failed or discarded approaches outlined in the docs.
- If file edits are required, use Git for backup/restore: commit changes or create a backup branch; if Git is unavailable, execute a local backup using the format: filename.ddmmyy-hhmmss
- Explicitly flag any stale or conflicting documentation found during this read phase.
```

---














# Prompt 2 — Operating Prompt

Use after bootstrap.

```text
Session Operating Rules:
1. Architectural Discipline: Prefer minimal, highly verifiable changes. Eliminate speculative refactoring or "pre-optimization."
2. Structural Invariance: Maintain strict consistency with ARCHITECTURE.md and DECISIONS.md.
3. Impact Analysis: Before altering any file, map its dependencies and list potential regressions.
4. Enforce a strict file-isolation workspace: work only on the targeted file under modification. External files may only be read contextually to satisfy Rule 3, using the transient method defined in Rule 5. 
5. Never maintain multi-file buffers in your active generation state. If another file must be read for dependency context, extract only the core interface/signature instantly, and do not reference or re-read the rest of that file's body in subsequent turns.
6. After significant milestones or before wrapping up the session, you must synchronize the state docs via git commit. Maximize durable project intelligence per token by using ultra-dense bullet points, removing narrative prose, and using tables where appropriate.

Update only when relevant:
- PROJECT_STATE.md (For changes to current objective, task lists, or immediate focus)
- DECISIONS.md (Log the technical WHY behind major architectural pivots)
- KNOWN_ISSUES.md (Log newly discovered bugs or technical debt)

Session Handover Output: Before terminating the session, output a concise summary enclosed strictly in <session_handover> tags. Do not include conversational filler outside of these tags.
```

---







# Documentation Context Optimization Prompt

```text id="ntm1s8"
Review all docs/*.md files for context-window efficiency and long-session AI usability.

Goals:
- Reduce token usage
- Remove redundancy
- Improve information density
- Preserve critical architectural/project knowledge
- Improve AI session bootstrap speed
- Improve long-term maintainability

For each file:

1. Identify:
   - duplicated information,
   - stale content,
   - verbose explanations,
   - low-value prose,
   - repeated architecture descriptions,
   - unnecessary examples,
   - overlapping sections across files.
 
2. Compress aggressively:
   - replace paragraphs with concise bullet points,
   - convert narrative into structured data,
   - shorten repeated wording,
   - remove conversational language,
   - remove unnecessary formatting/noise.

3. Separate:
   - stable long-term knowledge,
   - active short-term state,
   - temporary session notes,
   - historical/archive material.

4. Remove:
   - duplicated instructions already covered elsewhere,
   - generic engineering advice,
   - obvious explanations,
   - repeated constraints,
   - outdated completed tasks,
   - unnecessary historical discussion.

5. Prefer:
   - Ultra-compact Markdown tables for structured data (e.g., task status, system states).
   - Flat, high-signal key-value pairs instead of nested lists.
   - Strict technical facts, removing conversational transitions or pleasantries.
   - Dense, technical shorthand where clarity isn't compromised.

6. Produce:
   - The fully optimized, compressed text of each target file.
   - A brief summary tracking: [File] | [Original Tokens] | [Optimized Tokens] | [Estimated % Reduction]
   - Identification of any remaining high-cost documentation blocks.

7. Files:
   Please remove the extra md files and move the contents to the appropriate files below.
     - ARCHITECTURE.md
     - CHANGELOG.md
     - DECISIONS.md
     - KNOWN_ISSUES.md
     - NOW.md
     - PROJECT_STATE.md
     - TASKS.md

Optimization priority:
maximize durable project intelligence per token.
- When optimizing docs, commit changes via Git for traceability.
```












# ONLINE-TRADER-3 COMPREHENSIVE SYSTEM REVIEW

You are acting as a Senior Quantitative Trading Engineer, Python Architect, Production Reliability Engineer, and Trading Risk Auditor.

Your task is NOT to modify code.

Your task is to perform a comprehensive review of the project and produce an actionable assessment report.

## Files To Review

Review ALL available information including:

* docs/*.md
* README files
* Python source code (*.py)
* Configuration files
* Latest Summarize Performance Report
* Latest trader.log
* Reflection reports
* Strategy reports
* Trade history outputs
* Any generated metrics or analytics files

Treat the Summarize Performance Report as the primary source of trading behaviour.

Treat trader.log as the primary source of runtime behaviour.

Treat source code as the primary source of implementation behaviour.

---

# Review Objectives

Provide findings in the following sections.

## SECTION 1 - Executive Summary

Provide:

* Overall system health score (0-100)
* Trading strategy maturity score (0-100)
* Production readiness score (0-100)
* Risk management score (0-100)
* Data quality score (0-100)

Explain each score.

---

## SECTION 2 - Critical Problems

Identify issues that could:

* Cause financial loss
* Cause runaway trading
* Cause excessive drawdown
* Cause strategy degradation
* Cause reflection loops
* Cause incorrect position sizing
* Cause risk control failures
* Cause data corruption
* Cause incorrect performance reporting

For each issue provide:

Severity:

* Critical
* High
* Medium
* Low

Include:

* Description
* Why it matters
* Evidence
* Recommended action

---

## SECTION 3 - Trading Performance Review

Review actual performance.

Analyse:

* Win rate
* Loss rate
* Profit factor
* Expectancy
* Drawdown
* Average winner
* Average loser
* Risk/reward ratio
* Trade frequency
* Capital growth
* Capital decline

Determine:

* Is the strategy profitable?
* Is profitability statistically meaningful?
* Is there sufficient trade volume?
* Are results likely due to luck?
* Are results stable?

---

## SECTION 4 - Strategy Quality Assessment

Evaluate:

* Entry logic
* Exit logic
* Position sizing
* Reflection system
* Self-improvement process
* Trade selection quality
* Overfitting risk
* Underfitting risk
* Market adaptability

Identify any signs of:

* Curve fitting
* Strategy drift
* Excessive optimisation
* Reflection bias
* Feedback loop failures

---

## SECTION 5 - Runtime & Operational Review

Review trader.log and runtime behaviour.

Identify:

* Errors
* Exceptions
* API failures
* Data quality issues
* Missing data
* Slow execution
* Retry loops
* Stability concerns
* Resource issues

Provide evidence from logs.

---

## SECTION 6 - Risk Management Review

Assess:

* Maximum trade sizing
* Position exposure
* Consecutive losses
* Drawdown controls
* Capital preservation
* Trade limits
* Daily limits
* Emergency stop mechanisms

State whether risk controls appear adequate.

---

## SECTION 7 - Missing Metrics & Missing Information

This is a high priority section.

Review the latest Summarize Performance Report and determine:

1. What information is currently missing?
2. What information would significantly improve future recommendations?
3. What metrics should be added?
4. What diagnostics should be added?
5. What reflection metrics should be added?

For each missing item provide:

* Metric name
* Why it matters
* Example output
* Priority (High/Medium/Low)

Focus on metrics that improve decision making.

Avoid vanity metrics.

---

## SECTION 8 - Potential Upgrades

Do NOT implement.

Do NOT generate code.

Provide potential upgrades only.

Categorise as:

### High Impact

Likely to materially improve profitability, safety, or reliability.

### Medium Impact

Useful improvements.

### Low Impact

Nice-to-have improvements.

For each upgrade provide:

* Expected benefit
* Complexity
* Risk
* Recommendation

---

## SECTION 9 - Next Actions

Provide:

### Immediate Actions (Next Session)

Top 5 actions.

### Short-Term Actions

Next 1-2 weeks.

### Long-Term Actions

Future roadmap.

Prioritise by expected value.

---

## SECTION 10 - Questions For The Owner

List any missing information that prevents stronger recommendations.

Ask specific questions only.

Do not ask questions that can be answered from the project files.

---

# Additional Analysis Required

Specifically determine whether the Summarize Performance Report includes enough information to answer:

* Why trades win
* Why trades lose
* Whether the strategy is improving
* Whether reflection is helping
* Whether risk is improving
* Whether profitability is improving
* Whether capital efficiency is improving

If any answer cannot be confidently determined, explain exactly what additional data should be included in future reports.

---

# Output Format

Use the following structure:

1. Executive Summary
2. Critical Problems
3. Trading Performance Review
4. Strategy Quality Assessment
5. Runtime & Operational Review
6. Risk Management Review
7. Missing Metrics & Missing Information
8. Potential Upgrades
9. Next Actions
10. Questions For The Owner

Be evidence-based.

Avoid cosmetic suggestions.

Prioritise issues that affect profitability, safety, reliability, risk management, and learning quality.

Do not generate code unless explicitly requested.

