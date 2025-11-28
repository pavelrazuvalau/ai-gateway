# Implementation Change History

## 📊 Metadata

**Artifact Version:** 0.1.9  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Git-like history of completed changes  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) contain data AND copied instructions (for self-sufficiency). Instructions section will be copied from this template.  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

---

## 📑 Index by Phases and Steps

**Quick Reference:** This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT). For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

**Quick navigation:**
- **Phase X: [Name]**
  - Step X.Y: [Name] (line ~N)

---

## Entry Format

Each entry answers questions: **WHAT** was done, **WHY** it was done this way, **WHAT** result

### ✅ Completed Entry Format

```
## YYYY-MM-DD - Phase X, Step X.Y

### ✅ Completed

**Description:**
[Brief summary of completed work]

**Changes:**
- `file1.[ext]`: [Specific change 1]
- `file2.[ext]`: [Specific change 2]

**Why this solution:**
[Explanation of approach choice, alternatives considered and rejected]

**Result:**
- [Measurable result 1]
- [Measurable result 2]

**Related:** QX.Y in @*_QUESTIONS.md (if any)
```

**Required fields:**
- Date and phase/step reference in header
- Description: Brief summary
- Changes: Specific files with changes (use backticks for file paths)
- Why this solution: Explanation with alternatives considered
- Result: Measurable/verifiable outcomes
- Related: Links to questions if applicable

### ❌ Stopped Entry Format

```
## YYYY-MM-DD - Phase X, Step X.Y - 🔴 BLOCKER

### ❌ Stopped

**Reason for blocking:**
[What prevented continuation]

**Blocker type:** 🔍 Requires user clarification | 🏗️ Architectural problem | 🐛 Bug discovered | 📊 Requirements unclear | 🤔 Requires deeper analysis

**Created question:** QX.Y in @*_QUESTIONS.md

**Completed before blocking:**
- [Partial work 1]

**Expected actions:**
[What is needed to unblock]
```

**Required fields:**
- Reason for blocking
- Blocker type (use blocker type icons)
- Created question (link to QUESTIONS)
- Completed before blocking (if any)
- Expected actions

### 🔧 Approach Changed Entry Format

```
## YYYY-MM-DD - Phase X, Step X.Y - 🔄 CORRECTION

### 🔧 Approach Changed

**Original plan:**
[What was planned]

**Why changed:**
[Rationale for correction - new information, discovered problem]

**New approach:**
[Updated solution]

**Related questions:** QX.Y (answered)
```

**Required fields:**
- Original plan
- Why changed (rationale)
- New approach
- Related questions (if any)

### 📐 Formatting Reference

**Date format:** YYYY-MM-DD (e.g., 2025-01-27)

**File paths:** Use backticks: `` `path/to/file.[ext]` ``

**Links:** Use `@[ARTIFACT_NAME]` notation:
- `@[TASK_NAME]_QUESTIONS.md` - link to QUESTIONS
- `QX.Y in @[TASK_NAME]_QUESTIONS.md` - link to specific question

**Anchor Links for Navigation:**
- Anchor links provide fast navigation within artifacts
- Format: `[Text](#anchor-name)` where anchor is generated from heading text
- Markdown automatically creates anchors from headings (lowercase, spaces to hyphens)
- Example: `## YYYY-MM-DD - Phase 1, Step 1.1` → anchor `#yyyy-mm-dd---phase-1-step-11`
- Use anchor links in index/navigation sections for quick access to entries

**Entry types:**
- ✅ Completed - Step completed successfully
- ❌ Stopped - Work stopped due to blocker
- 🔧 Approach Changed - Initial approach changed

**Blocker types:**
- 🔍 Requires user clarification
- 🏗️ Architectural problem
- 🐛 Bug discovered
- 📊 Requirements unclear
- 🤔 Requires deeper analysis

---

## 🤖 Instructions for AI agent

**Important:** This section is part of the template (View layer). When creating actual artifacts (Model layer), **COPY this instruction section** into the artifact at the end of the document. This ensures that instructions for working with the artifact are always available within the artifact itself, making it self-sufficient and independent of external prompts or templates.

**⚠️ IMPORTANT FOR CREATION AGENT (planning agent):**

These instructions are for FUTURE USE by the execution agent.
DO NOT try to execute these instructions while creating the artifact.
Your job is to COPY this entire section into the artifact as-is, at the end of the document.
These instructions will be used later when working with the artifact during execution phase.
Do NOT follow "How to update" or "When to update" instructions during artifact creation.

**Artifact System Overview:**

This artifact is part of a system of 4 required artifacts that work together:

1. **PLAN** (`*_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
2. **CHANGELOG** (`*_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
3. **QUESTIONS** (`*_QUESTIONS.md`) - Knowledge base for doubts and solutions. Contains active questions (blockers) and resolved questions.
4. **SESSION_CONTEXT** (`*_SESSION_CONTEXT.md`) - Current work state. Contains temporary notes, intermediate decisions, and active context.

**Artifact Relationships:**
- PLAN references blockers in QUESTIONS and recent changes in CHANGELOG
- CHANGELOG entries link to PLAN steps and related questions in QUESTIONS
- QUESTIONS link to PLAN steps and CHANGELOG entries where solutions were applied
- SESSION_CONTEXT tracks current PLAN phase/step and active questions

**When to update artifacts:**
- **PLAN**: When step status changes, when starting/completing steps, when blocked
- **CHANGELOG**: When step completes, when question is resolved, when approach changes
- **QUESTIONS**: When creating new question, when answering question
- **SESSION_CONTEXT**: When starting step, when discovering blocker, when completing step, when making intermediate decisions

**How to read artifacts (created from this template):**
1. Entries are sorted by date (newest first, chronological order)
2. Each entry contains: Description, Changes, Why this solution, Result
3. Use index by phases/steps for quick search
4. Check links to related questions in entries
5. Entry types: ✅ Completed, ❌ Stopped, 🔧 Approach Changed

**How to update artifacts (created from this template):**
1. When step completes → add new entry at the top (after metadata):
   - Add entry immediately after metadata section
   - Use format: `## YYYY-MM-DD - Phase X, Step X.Y`
   - Include all required sections (see "Entry Format" section above)
2. Entry format: `## YYYY-MM-DD - Phase X, Step X.Y`
   - Date format: YYYY-MM-DD
   - Phase/Step reference: Phase X, Step X.Y
3. Required sections for ✅ Completed entries:
   - Description (brief summary)
   - Changes (specific files with changes)
   - Why this solution (explanation with alternatives considered)
   - Result (measurable/verifiable outcomes)
   - Related (links to questions if any)
4. Entry types:
   - ✅ Completed: Step completed successfully
   - ❌ Stopped: Work stopped due to blocker (include reason, question link)
   - 🔧 Approach Changed: Initial approach changed (include original plan, why changed, new approach)
5. Add links to related questions (if any):
   - Format: `QX.Y in @*_QUESTIONS.md`
6. Update index by phases/steps:
   - Add entry to index section
   - Format: `- Step X.Y: [Name] (line ~N)`

**Formatting rules:**
- Use exact entry format as defined in "Entry Format" section above
- Date format: YYYY-MM-DD
- File paths in Changes section: use backticks `file.[ext]`
- Links use `@[ARTIFACT_NAME]` notation
- Entry types use icons: ✅ ❌ 🔧

**When to use this file:**
- When checking history of completed changes
- When understanding decision rationale
- When searching for examples of completed steps
- When checking related questions
- When documenting completed work

**Related artifacts:**
- `*_PLAN.md` - for understanding current state and next steps
- `*_QUESTIONS.md` - for checking active questions mentioned in entries
- `*_SESSION_CONTEXT.md` - for current session context
