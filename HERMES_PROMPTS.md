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


