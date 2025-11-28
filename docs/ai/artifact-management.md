# Artifact Management System Prompts

**Version:** 2.3  
**Date:** 2025-01-27  
**Purpose:** Documentation explaining the artifact management system architecture with separation of concerns

---

## Overview

The artifact management system follows MVC-like architecture with clear separation of concerns:

1. **System Prompts (Controller)** - Logic, procedures, workflow
   - **`impl-planner.agent.md`** (v1.3) - Planning and artifact creation
   - **`vibe-coder.agent.md`** (v1.4) - Execution and artifact maintenance

2. **Template Files (View)** - Formatting, structure, presentation
   - `docs/ai/IMPLEMENTATION_PLAN.md` - PLAN artifact template
   - `docs/ai/IMPLEMENTATION_CHANGELOG.md` - CHANGELOG artifact template
   - `docs/ai/IMPLEMENTATION_QUESTIONS.md` - QUESTIONS artifact template
   - `docs/ai/IMPLEMENTATION_SESSION_CONTEXT.md` - SESSION_CONTEXT artifact template

3. **Artifacts (Model)** - Data and context
   - PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT artifacts

This separation provides clearer responsibilities, eliminates duplication, and ensures consistent formatting.

---

## When to Use Which Prompt

### Use `impl-planner.agent.md` when:

- Starting a new task from scratch
- Need to analyze codebase and create a plan
- Want to break down a task into phases and steps
- Need to create all 4 artifacts (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT)
- Identifying questions and blockers upfront
- Planning phase of work

**Input**: Task description, codebase  
**Output**: Complete set of artifacts ready for execution

### Use `vibe-coder.agent.md` when:

- Artifacts already exist (created by planner or manually)
- Ready to execute tasks following a plan
- Need to implement code changes
- Updating artifacts during work
- Handling blockers and questions during execution
- Execution phase of work

**Input**: Existing artifacts (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT)  
**Output**: Code changes and updated artifacts

---

## Workflow

### Typical Workflow

1. **Planning Phase** (use `impl-planner.agent.md`):
   - Receive task description
   - Analyze codebase
   - Create PLAN with phases and steps
   - Create CHANGELOG (empty, ready for entries)
   - Create QUESTIONS with identified questions
   - Create SESSION_CONTEXT (empty, ready for use)
   - All artifacts ready for execution

2. **Execution Phase** (use `vibe-coder.agent.md`):
   - Read existing artifacts
   - Follow core workflow: Analysis → Solution → Action → Documentation
   - Follow PLAN step by step
   - Implement code changes
   - Update artifacts as work progresses
   - Handle blockers by creating questions (STOP rules apply)
   - Complete steps and document in CHANGELOG

### Iterative Workflow

You can switch between prompts as needed:
- If new questions arise during execution → can use planner to update PLAN
- If plan needs major restructuring → can use planner to revise artifacts
- Execution can pause and resume using same artifacts

---

## Separation of Concerns

### System Prompts (Controller)
**Responsibility:** Logic, procedures, workflow, validation

**What they contain:**
- Logic: What to do, when to do it, how to validate
- Procedures: Step-by-step instructions for creating/updating artifacts
- Workflow: Analysis → Solution → Action → Documentation
- Validation: Checklists and criteria

**What they DON'T contain:**
- Formatting rules (icons, statuses, structure)
- Examples of formatting
- Detailed structure definitions

**Files:**
- `impl-planner.agent.md` (v1.3) - Planning and artifact creation
- `vibe-coder.agent.md` (v1.4) - Execution and artifact maintenance

### Template Files (View)
**Responsibility:** Formatting, structure, presentation, examples

**What they contain:**
- Formatting rules: Icons, statuses, priority indicators
- Structure definitions: Sections, metadata fields, entry formats
- Instructions: How to read, how to update, when to use
- Examples: Format examples for each artifact type
- Formatting reference: Complete formatting guide
- Navigation sections: Quick navigation for humans (e.g., "Current Focus" section)

**What they DON'T contain:**
- Logic or procedures
- Workflow definitions
- Validation rules

**Files:**
- `docs/ai/IMPLEMENTATION_PLAN.md` - PLAN template
- `docs/ai/IMPLEMENTATION_CHANGELOG.md` - CHANGELOG template
- `docs/ai/IMPLEMENTATION_QUESTIONS.md` - QUESTIONS template
- `docs/ai/IMPLEMENTATION_SESSION_CONTEXT.md` - SESSION_CONTEXT template

### Artifacts (Model)
**Responsibility:** Data and context

**What they contain:**
- Current state: Status, progress, context
- History: Completed work, decisions, solutions
- Questions: Active and resolved questions
- Context: Current session state
- Instructions: Copied instruction section from template (for self-sufficiency)

## Key Differences

| Aspect | impl-planner.agent.md | vibe-coder.agent.md |
|--------|----------------------|---------------------|
| **Version** | 1.3 | 1.4 |
| **Focus** | Analysis and planning | Implementation and execution |
| **Input** | Task description, codebase | Existing artifacts |
| **Output** | Complete artifacts | Code changes + updated artifacts |
| **Status Rules** | Definitions only | Full transition rules |
| **Procedures** | Creation procedures | Update procedures |
| **Workflow** | Planning workflow | Core workflow: Analysis → Solution → Action → Documentation |
| **Stop Rules** | Not applicable | Explicit STOP rules for blockers and deep analysis |
| **Assumptions** | No artifacts exist | Artifacts already exist |

---

## Shared Elements

Both prompts share:
- Reference to template files in `docs/ai/` directory
- Cross-artifact link format (`@[ARTIFACT_NAME]` notation)
- Universalization principles
- Quality criteria (adapted for creation vs. updates)
- Key principles (adapted for planning vs. execution)

**Important:** All formatting rules (icons, statuses, structure, examples) are in template files, not in system prompts.

## Key Features

### impl-planner.agent.md (v1.3)
- Code-first analysis approach (repository files as primary source)
- Creates all 4 artifacts from scratch
- Identifies questions and blockers upfront
- Universal and technology-agnostic
- References template files for formatting (no formatting rules in prompt)

### vibe-coder.agent.md (v1.4)
- **Core Workflow**: Analysis → Solution → Action → Documentation
- **Stop Rules**: Explicit rules for when to STOP (blockers, deep analysis, uncertainty)
- Artifacts as source of truth
- Detailed update procedures for each artifact
- Status transition rules
- References template files for formatting (no formatting rules in prompt)

---

## Template Files

Both prompts reference template files in `docs/ai/`:
- `IMPLEMENTATION_PLAN.md` - PLAN artifact template
- `IMPLEMENTATION_CHANGELOG.md` - CHANGELOG artifact template
- `IMPLEMENTATION_QUESTIONS.md` - QUESTIONS artifact template
- `IMPLEMENTATION_SESSION_CONTEXT.md` - SESSION_CONTEXT artifact template

**Template files contain:**
- Complete formatting rules (icons, statuses, priority indicators)
- Structure definitions (sections, metadata fields, entry formats)
- Instructions for AI agents (how to read, how to update, when to use)
- Formatting reference (complete formatting guide)
- Examples for each artifact type
- Navigation sections (e.g., "Current Focus" for quick access to current step/question)

**Template files are the source of truth for formatting and instructions.** System prompts contain only logic and procedures, with references to templates for formatting details.

**Important MVC principle:** 
- **Templates (View)** contain instructions and structure for copying into artifacts
- **Artifacts (Model)** contain data AND copied instructions (for self-sufficiency)
- When creating artifacts, **COPY the instruction section** ("🤖 Instructions for AI agent") from templates into artifacts
- This ensures artifacts are self-sufficient and can be used independently of templates
- Instructions in artifacts are copied from templates, making templates the source of truth

---

## Migration from Old Prompt

The original `artifact-management.agent.md` (v1.0) combined both planning and execution. It has been split into:

- **Planning parts** → `impl-planner.agent.md`
- **Execution parts** → `vibe-coder.agent.md`

If you have existing artifacts created with the old prompt, they are compatible with the new execution prompt (`vibe-coder.agent.md`).

---

## Architecture Benefits

**Separation of Concerns:**
- System prompts focus on logic and procedures
- Template files focus on formatting, structure, and instructions (source of truth)
- Artifacts contain data AND copied instructions (for self-sufficiency)
- Instructions are copied from templates to artifacts, maintaining templates as source of truth
- Clear boundaries of responsibility

**MVC Principle:**
- **Model (Artifacts)**: Data (metadata, phases, steps, entries, questions, context) AND copied instructions
- **View (Templates)**: Formatting, structure, instructions for agents (source of truth for copying)
- **Controller (System Prompts)**: Logic, procedures, workflow

**Critical Rule:** When creating artifacts from templates, **COPY the instruction section** ("🤖 Instructions for AI agent") from templates into artifacts. This ensures artifacts are self-sufficient and can be used independently. Templates remain the source of truth for instructions, which are copied into artifacts for convenience and independence.

**Maintainability:**
- Formatting changes only require template updates (instructions are copied from templates)
- Logic changes only require system prompt updates
- Templates are the source of truth for formatting and instructions
- When templates are updated, new artifacts will include updated instructions
- Existing artifacts retain their copied instructions (may need manual update if template changes significantly)
- Easier to understand and modify

**Consistency:**
- Same templates used for both planning and execution
- Consistent formatting across all artifacts
- Clear formatting reference in templates
- No conflicting formatting rules
- Instructions are copied from templates to artifacts, ensuring consistency

## Notes

- Both prompts are independent and can be used separately
- Planning prompt produces artifacts ready for execution
- Execution prompt works with any properly formatted artifacts
- Template files serve as single source of truth for formatting and instructions
- Both prompts reference templates for formatting details and instructions
- System prompts contain only logic, procedures, and workflow
- Both prompts are universal and technology-agnostic

**Critical MVC Rule:**
- When creating artifacts from templates, **COPY the instruction section** ("🤖 Instructions for AI agent") from templates into artifacts
- Artifacts (Model) contain data (metadata, phases, steps, entries, questions, context) AND copied instructions
- Instructions are part of templates (View) and are copied into artifacts for self-sufficiency
- This ensures artifacts are self-sufficient and can be used independently of templates
- Templates remain the source of truth for instructions, which are copied into artifacts
- This maintains clean separation: Model = data + copied instructions, View = instructions/formatting (source of truth), Controller = logic

---

**End of Documentation**
