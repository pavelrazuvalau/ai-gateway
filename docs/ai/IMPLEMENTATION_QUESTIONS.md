# Implementation Questions and Clarifications

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Repository for doubts and solutions  
**Status:** Template file (View layer)  
**How to use:** See "🤖 Instructions for you" at the end

---

## 🎯 Current Focus

> **Requires Your Answer:** [QX.Y: Question Title](#qxy-question-title-phase-x-step-y)  
> **Priority:** 🔴 High | 🟡 Medium | 🟢 Low  
> **Status:** ⏳ Pending

> **Note:** If no active questions, show: "No active questions requiring your answer"

---

## ❓ Active Questions

> **📌 Sorting:** 🔴 High → 🟡 Medium → 🟢 Low

<!-- Questions are added here - sorted by priority -->
<!-- Use formats from "📐 Question Formats Reference" section below -->

---

## ✅ Answered Questions

<!-- Resolved questions are moved here -->
<!-- Use answered format from "📐 Question Formats Reference" section below -->

---

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 🤖 AI REFERENCE SECTION - Templates, formats, and instructions below        -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

## 📐 Question Formats Reference

> **Note:** This section contains templates for AI. For humans, see actual questions above.

### Active Question Format

```
### QX.Y: [Question Title] (Phase X, Step Y)

**Phase/Step:** Phase X, Step Y  
**Creation Date:** YYYY-MM-DD  
**Priority:** 🔴 High | 🟡 Medium | 🟢 Low

**Context:**
[Detailed description of situation that caused the question]

**Question:**
[Specific question requiring clarification]

**Why important:**
[Explanation of how answer will affect further work]

**Context analysis:**
- [What was analyzed: code, documentation, artifacts, SESSION_CONTEXT]
- [What was found: patterns, libraries, existing solutions]
- [Can answer be determined from context: yes/no/partially]

**Solution options:**

- [ ] **Option 1:** [Description] - pros/cons
- [x] **⭐ Option 2 (Recommended):** [Description] - pros/cons
- [ ] **Option 3:** [Description] - pros/cons

**Recommendation and justification:**
⭐ **Option X is recommended** for the following reasons:
- **Comparison with Option Y:** [Comparison]
- **Advantages of recommended option:** [Advantages]
- **When other options are preferable:** [When other options are better]

**Your answer:**
- [ ] Use one of the options above (check your choice in Solution options)
- [ ] Provide custom answer:

```
[Place for your answer]
```

**Status:** ⏳ Pending
```

**Required fields:**
- Phase/Step, Creation Date, Priority
- Context, Question, Why important
- Context analysis (MANDATORY)
- Solution options with pros/cons (MANDATORY)
- Recommendation and justification (if options can be proposed)
- Your answer (interactive markup)
- Status: ⏳ Pending

**Special case (user input required):**
```
**⚠️ User input required:**
- Context analysis cannot determine the answer
- Please provide your answer below:
```

**Question criteria:**
- Cannot be resolved by code analysis alone
- Requires user input, architectural decision, or external information
- Has clear impact on work progress

### Answered Question Format

```
### QX.Y: [Question Title]

**Answer:** [Accepted solution]  
**Rationale:** [Why this was chosen]  
**Closing Date:** YYYY-MM-DD  
**Applied in:** [CHANGELOG entry link]
```

---

## 📐 Formatting Reference

### Status Icons

**For Questions:**
- ⏳ **Pending** - Question created, waiting for answer
- ✅ **Resolved** - Question answered, solution documented, moved to resolved section

### Priority Icons

- 🔴 **High** - Blocks work, cannot proceed
- 🟡 **Medium** - Affects work, can proceed with assumptions
- 🟢 **Low** - Optimization, can proceed without answer

**Priority sorting:** Questions must be sorted by priority: 🔴 High → 🟡 Medium → 🟢 Low

### Blocker Types

🔍 **Requires user clarification** - needs clarification of context or requirements  
🏗️ **Architectural problem** - design contradiction  
🐛 **Bug discovered** - technical blocker  
📊 **Requirements unclear** - needs clarification of business logic  
🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation

### Cross-Artifact Links

**Link format:** `@[ARTIFACT_NAME]` notation

**Examples:**
- `@[TASK_NAME]_PLAN.md` - link to PLAN
- `@[TASK_NAME]_CHANGELOG.md (Phase 1, Step 1.1)` - link to specific entry
- `QX.Y in @[TASK_NAME]_QUESTIONS.md` - link to question

**Rules:**
- Always use artifact file name
- Include phase/step or question identifier when linking to specific content
- Use consistent format across all artifacts
- Verify links point to existing content

### Anchor Links for Navigation

**Concept**: Anchor links provide fast navigation. They enable quick jumping to specific sections within artifacts.

**Format**: `[Text](#anchor-name)` where anchor is generated from heading text.

**Anchor Generation Rules**:
- Markdown automatically creates anchors from headings
- Format: lowercase, spaces converted to hyphens, special characters removed
- Example: `### Q2.1: E2E Tests - Provider Mocks` → anchor `#q21-e2e-tests---provider-mocks`
- For headings with special characters, use the exact heading text and let Markdown generate the anchor

**Usage**:
- Use anchor links in "Current Focus" and "Quick Navigation" sections
- Update anchor links when current step/question changes
- Anchor links enable both agents and humans to quickly navigate to relevant sections

**Example**:
- In QUESTIONS artifact "Current Focus" section: `[Q2.1: Question Title](#q21-question-title-phase-2-step-1)`

**Important**: Always verify anchor links point to existing headings in the artifact.

---

## 🤖 Instructions for you

> **Quick Reference:** Questions go in "❓ Active Questions" section. Templates are in "📐 Question Formats Reference" section above.

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

**When to update:**
- When creating new question
- When answering question

**How to update:**

1. **New question** → add to "❓ Active Questions":
   - Use format from "📐 Question Formats Reference"
   - Sort by priority: 🔴 → 🟡 → 🟢
   - Update "🎯 Current Focus" section

2. **Answer question** → **MOVE to "✅ Answered Questions" (NOT copy!)**:
   - Remove from Active Questions
   - Add with answer to Answered Questions
   - Update "🎯 Current Focus" (show next or "No active questions")

**Current Focus rule:** Show highest priority active question (🔴 → 🟡 → 🟢)

**Technical procedures (for long lists):**
- Create questions one at a time via `search_replace`
- Verify success via `read_file` after each question

**Question types:**
- 🔍 Requires user clarification
- 🏗️ Architectural problem
- 🐛 Bug discovered
- 📊 Requirements unclear
- 🤔 Requires deeper analysis

**Related artifacts:**
- `*_PLAN.md` - question context (phase/step)
- `*_CHANGELOG.md` - applied solutions
- `*_SESSION_CONTEXT.md` - session context
