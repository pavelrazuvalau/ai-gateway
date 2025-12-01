# Implementation Change History

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Git-like history of completed changes  
**Status:** Template file (View layer)  
**How to use:** See "🤖 Instructions for you" at the end

---

## 📑 Index by Phases and Steps

**Quick navigation:**
- **Phase X: [Name]**
  - Step X.Y: [Name] → [link to entry](#anchor)

---

## 📜 Change History

<!-- Entries are added here - newest first -->
<!-- Use entry formats from "📐 Entry Formats Reference" section below -->

---

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 🤖 AI REFERENCE SECTION - Templates, formats, and instructions below        -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

## 📐 Entry Formats Reference

> **Note:** This section contains templates for AI. For humans, see actual entries in "Change History" above.

Each entry answers: **WHAT** was done, **WHY** this way, **WHAT** result

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

**Related:** QX.Y in @*_QUESTIONS.md (include this field only if question exists for this step)
```

**Required fields:**
- Date and phase/step reference in header
- Description: Brief summary
- Changes: Specific files with changes (use backticks for file paths)
- Why this solution: Explanation with alternatives considered
- Result: Measurable/verifiable outcomes
- Related: Links to questions (include this field only if question exists for this entry)

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
- Completed before blocking: List all partial work completed before blocker was discovered (include this field only if partial work exists)
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
- Related questions: QX.Y in @*_QUESTIONS.md (include this field only if question exists for this entry)

### Formatting Rules

**Date format:** YYYY-MM-DD (e.g., 2025-01-27)

**File paths:** Use backticks: `` `path/to/file.[ext]` ``

**Links:** Use `@[ARTIFACT_NAME]` notation:
- `@[TASK_NAME]_QUESTIONS.md` - link to QUESTIONS
- `QX.Y in @[TASK_NAME]_QUESTIONS.md` - link to specific question

**Anchor Links:**
- Format: `[Text](#anchor-name)` where anchor is generated from heading text
- Markdown automatically creates anchors from headings (lowercase, spaces to hyphens)
- Example: `## YYYY-MM-DD - Phase 1, Step 1.1` → anchor `#yyyy-mm-dd---phase-1-step-11`

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

## 🤖 Instructions for you

> **Quick Reference:** This artifact is part of a 4-artifact system. Entries go in "📜 Change History" section. Entry templates are in "📐 Entry Formats Reference" section above.

**Template Contract:**
- Template (View layer) = Structure and formatting rules
- Artifact (Model layer) = Data + Copied instructions (self-sufficient)
- When creating artifacts: COPY this entire section into the artifact at the end

**Artifact System (4 artifacts):**

| Artifact | Purpose | Key Content |
|----------|---------|-------------|
| PLAN | Execution roadmap | Phases, steps, status |
| CHANGELOG | Change history | What, why, result |
| QUESTIONS | Blockers & solutions | Active/resolved questions |
| SESSION_CONTEXT | Current state | Temporary notes, decisions |

**Artifact Relationships:**
- PLAN → references blockers in QUESTIONS, recent changes in CHANGELOG
- CHANGELOG → links to PLAN steps and QUESTIONS
- QUESTIONS → links to PLAN steps and CHANGELOG entries
- SESSION_CONTEXT → tracks current PLAN phase/step

**When to update:**
- When step completes
- When question is resolved
- When approach changes

**How to update:**
1. Add new entry in "📜 Change History" section (newest first)
2. Use format from "📐 Entry Formats Reference" section
3. Update "📑 Index by Phases and Steps" section

**Entry location:** Add immediately after `## 📜 Change History` heading

**Index format:** `- Step X.Y: [Name] → [link](#anchor)`

**Technical procedures (for long lists):**
- Create entries one at a time via `search_replace`
- Verify success via `read_file` after each entry
- If > 3-5 entries → use sequential filling

**Related artifacts:**
- `*_PLAN.md` - current state and next steps
- `*_QUESTIONS.md` - active questions
- `*_SESSION_CONTEXT.md` - session context
