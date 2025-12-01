# [Task Name]

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Purpose:** [Purpose of this plan]  
**Status:** 🟢 COMPLETED | 🟡 IN PROGRESS | 🔴 BLOCKED | 🔵 READY FOR WORK | ⚪ PENDING  
**Current Phase:** Phase X  
**Current Step:** Step X.Y  
**Last Update:** YYYY-MM-DD  
**How to use:** See "🤖 Instructions for you" at the end

---

## 🎯 Current Focus

> **Current Step:** [Phase X, Step Y: Step Name](#phase-x-step-xy-step-name)  
> **Status:** 🟡 IN PROGRESS | 🔴 BLOCKED | 🔵 READY FOR WORK | ⚪ PENDING  
> **Action Required:** [No action required | Answer question in @*_QUESTIONS.md (QX.Y) | Review and approve plan | Other specific action]

---

## 🎯 Description

[Brief description of the task, goals, and business value]

## 🚦 Quick Navigation

- **Start here:** Phase X, Step Y
- **Blockers:** See @*_QUESTIONS.md (section [X])
- **Recent changes:** See @*_CHANGELOG.md (entry from [date])

---

## Implementation Phases

### Phase X: [Phase Name]

**Context:** [Context of related tasks in this phase]  
**Goal:** [Expected outcome]  
**Status:** 🟢 COMPLETED | 🟡 IN PROGRESS | 🔴 BLOCKED | 🔵 READY FOR WORK | ⚪ PENDING

#### Step X.Y: [Step Name]

**Status:** ⚪ Pending | 🔵 Ready for Work | 🟡 In Progress | 🟢 Done | 🔴 Blocked

**What needs to be done:**
- [Specific action 1]
- [Specific action 2]

**Where to make changes:**
- Files: `path/to/file.[ext]`, `docs/section.md`
- Functions/Classes: `ClassName.method_name()`

**Why this approach:**
[Justification of approach - critical for understanding context and avoiding hallucinations]

**How:**
1. Action 1
2. Action 2
3. Action 3

**IMPACT:**
- [Measurable result 1]
- [Measurable result 2]
- [Measurable result 3]

**Completion criteria:**
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]

**Related questions:** QX.Y in @*_QUESTIONS.md

---

[Repeat structure for all phases and steps]

---

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 🤖 AI REFERENCE SECTION - Formats, rules, and instructions below            -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

## 📐 Formatting Reference

> **Note:** This section contains formatting rules for AI. For humans, see Implementation Phases above.

### Status Icons

**For PLAN artifact (overall status in Metadata section):**
- 🟡 **IN PROGRESS** - Plan is active and ready for execution (default when plan is created and ready)
- 🔴 **BLOCKED** - Plan execution blocked by unresolved question (at least one step is BLOCKED)
- 🟢 **COMPLETED** - All steps completed
- ⚪ **PENDING** - Plan creation not complete or prerequisites not met (rarely used)

**For Steps and Phases:**
- ⚪ **PENDING** / **Pending** - Future step, not yet reached in workflow (prerequisites not met, previous steps not completed)
- 🔵 **READY FOR WORK** / **Ready for Work** - Next step, prerequisites met, ready to start work (previous step completed)
- 🟡 **IN PROGRESS** / **In Progress** - Actively working on this step, completion criteria are being worked on
- 🔴 **BLOCKED** / **Blocked** - Cannot proceed due to blocking issue, question created in QUESTIONS, waiting for resolution
- 🟢 **COMPLETED** / **Done** - All completion criteria met, changes documented in CHANGELOG

**Key clarification:**
- When plan is created and ready → PLAN status = 🟡 IN PROGRESS (not PENDING!)
- When step is next and ready to start → Step status = 🔵 READY FOR WORK (not PENDING!)
- When cannot proceed (any blocker) → Step status = 🔴 BLOCKED (not PENDING or READY FOR WORK!)
- ⚪ PENDING for steps means "future step, prerequisites not met", NOT "ready to work"
- 🔵 READY FOR WORK for steps means "next step, can start immediately"
- First step of a new plan should be 🔵 READY FOR WORK (plan is ready, first step can start)

**Types of blockers (all result in 🔴 BLOCKED):**
- Waiting for question answer (question in QUESTIONS artifact)
- Waiting for user decision/approval
- External dependency not available
- Technical issue blocking progress
- Missing information that requires clarification

**Status transition rules:**
- ⚪ PENDING → 🔵 READY FOR WORK (when prerequisites met, previous step completed)
- 🔵 READY FOR WORK → 🟡 IN PROGRESS (when work begins on next step)
- 🟡 IN PROGRESS → 🟢 COMPLETED (when all criteria met) + next step: PENDING → READY FOR WORK
- 🟡 IN PROGRESS → 🔴 BLOCKED (when blocker discovered)
- 🔴 BLOCKED → 🟡 IN PROGRESS (when question answered)

**For Questions:**
- ⏳ **Pending** - Question created, waiting for answer
- ✅ **Resolved** - Question answered, solution documented, moved to resolved section

### Priority Icons (for questions)

- 🔴 **High** - Blocks work, cannot proceed
- 🟡 **Medium** - Affects work, can proceed with assumptions
- 🟢 **Low** - Optimization, can proceed without answer

**Priority sorting:** Questions must be sorted by priority: 🔴 High → 🟡 Medium → 🟢 Low

### Blocker Type Icons (for questions)

- 🔍 **Requires user clarification** - needs clarification of context or requirements
- 🏗️ **Architectural problem** - design contradiction
- 🐛 **Bug discovered** - technical blocker
- 📊 **Requirements unclear** - needs clarification of business logic
- 🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation

### Structure Formatting

**Metadata section:**
- Must include: Artifact Version, Last Adaptation Date, Purpose, Status, Current Phase, Current Step, Last Update
- Status values: 🟢 COMPLETED | 🟡 IN PROGRESS | 🔴 BLOCKED | 🔵 READY FOR WORK | ⚪ PENDING

**Phase structure:**
- Format: `### Phase X: [Phase Name]`
- Must include: Context, Goal, Status
- Status uses same icons as steps

**Step structure:**
- Format: `#### Step X.Y: [Step Name]`
- Must include sections:
  - Status (with icon)
  - What needs to be done (bullet list)
  - Where to make changes (bullet list with files/functions)
  - Why this approach (paragraph)
  - How (numbered list of actions)
  - IMPACT (bullet list of measurable results)
  - Completion criteria (checklist)
  - Related questions: QX.Y in @*_QUESTIONS.md (include only if question exists for this step)

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
- Example: `#### Step 4.3: E2E Tests` → anchor `#step-43-e2e-tests`
- For headings with special characters, use the exact heading text and let Markdown generate the anchor

**Usage**:
- Use anchor links in "Current Focus" and "Quick Navigation" sections
- Update anchor links when current step/question changes
- Anchor links enable both agents and humans to quickly navigate to relevant sections

**Example**:
- In PLAN artifact "Current Focus" section: `[Phase 1, Step 1.1: Setup](#phase-1-step-11-setup)`
- In QUESTIONS artifact "Current Focus" section: `[Q2.1: Question Title](#q21-question-title-phase-2-step-1)`

**Important**: Always verify anchor links point to existing headings in the artifact.

---

## 🤖 Instructions for you

> **Quick Reference:** Phases and steps go in "Implementation Phases" section. Status icons and step format are in "📐 Formatting Reference" section above.

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

**⚠️ CRITICAL Execution Rule:**
- Work step-by-step with stops after each step/phase
- Wait for explicit user confirmation before proceeding

**When to update:**
- When step status changes
- When starting/completing steps
- When blocked

**How to update:**
1. When step status changes → update metadata at the beginning of file:
   - Update "Status" field
   - Update "Current Phase" and "Current Step" if changed
   - Update "Last Update" date
   - **Update "🎯 Current Focus" section** with new step link and status
2. When step completes → update step status (🟢 Done) and metadata:
   - Change step status to 🟢 Done
   - Update phase status if all steps complete
   - Update metadata fields
   - **Update "🎯 Current Focus" section**: If next step exists → show next step with status, if all steps completed → show "All steps completed"
3. When blocked → update status (🔴 Blocked) and add blocker reference:
   - Change step status to 🔴 Blocked
   - Update phase status to 🔴 BLOCKED (if this is the first blocked step in the phase, or if phase status is not already BLOCKED)
   - Add blocker reference to "🚦 Quick Navigation" section
   - Update metadata
   - **Update "🎯 Current Focus" section** with blocked status and set "Action Required: [specific action]" if needs user input (e.g., "Answer question in @*_QUESTIONS.md (QX.Y)")
4. When starting work → update status to 🟡 In Progress:
   - Change step status from 🔵 Ready for Work to 🟡 In Progress
   - Update metadata
   - **Update "🎯 Current Focus" section** with In Progress status
5. After changes → add entry to `*_CHANGELOG.md` (see CHANGELOG artifact instructions for procedure)

**How to update Current Focus section:**

**Simple rule:** Show the highest priority active step (first step that is not completed).

**Procedure:**
1. Find the first step with status: 🟡 IN PROGRESS, 🔴 BLOCKED, 🔵 READY FOR WORK, or ⚪ PENDING (in order of phases and steps)
2. Update "🎯 Current Focus" section with that step's link and status
3. If step is BLOCKED and needs user input → set "Action Required: [specific action]" (e.g., "Answer question in @*_QUESTIONS.md (QX.Y)")
4. If all steps completed → show "All steps completed"

**Examples:**

**Example 1: Step in progress**
```
## 🎯 Current Focus

> **Current Step:** [Phase 1, Step 1.1: Setup environment](#phase-1-step-11-setup-environment)
> **Status:** 🟡 IN PROGRESS
> **Action Required:** No action required
```

**Example 2: Step blocked**
```
## 🎯 Current Focus

> **Current Step:** [Phase 2, Step 2.3: Implement feature](#phase-2-step-23-implement-feature)
> **Status:** 🔴 BLOCKED
> **Action Required:** Answer question in @*_QUESTIONS.md (Q2.3)
```

**Example 3: All completed**
```
## 🎯 Current Focus

> **Status:** All steps completed
```

**Anchor link format:** `[Phase X, Step Y: Step Name](#phase-x-step-xy-step-name)` (Markdown auto-creates anchors from headings)
   - Example: `#### Step 4.3: E2E Tests` → `#step-43-e2e-tests`
   - For steps with special characters, use the exact heading text and let Markdown generate the anchor
   - To find the correct anchor, look at the actual heading in the document and use the format shown above

**Formatting rules:**
- Use exact status icons as defined in "📐 Formatting Reference" section above
- Follow structure: Phase → Step → What/Where/Why/How/IMPACT/Completion criteria
- Use consistent phase/step numbering (Phase X, Step X.Y)
- Links to other artifacts use `@[ARTIFACT_NAME]` notation
- Metadata fields must be updated when status changes

**Step Completeness Checklist:**

Each step MUST contain all fields:
- [ ] **What** - specific actions
- [ ] **Where** - files/functions
- [ ] **Why** - justification
- [ ] **How** - numbered steps
- [ ] **IMPACT** - measurable results
- [ ] **Completion criteria** - checkboxes

**When to use this file:**
- When starting work on a task from the plan
- When checking current project state
- When deciding on next step
- When updating work status
- When checking blockers and current progress

**Related artifacts:**
- `*_QUESTIONS.md` - for checking active questions and blockers
- `*_CHANGELOG.md` - for history of completed changes
- `*_SESSION_CONTEXT.md` - for current session context
