# Вопросы и уточнения по имплементации

## 📊 Metadata

**Artifact Version:** 2.0  
**Last Adaptation Date:** 2025-01-27  
**Purpose:** База знаний (сомнения и решения)  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

---

## 🎯 Current Focus

> **Requires Your Answer:** [Q2.1: E2E тесты - моки провайдеров (Этап 6.3)](#q21-e2e-тесты---моки-провайдеров-этап-63)  
> **Priority:** 🔴 High  
> **Status:** ⏳ Pending

---

## Активные вопросы (требуют ответа)

**Quick Reference:** This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT). For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

> **📌 Примечание:** Вопросы отсортированы по приоритетам: 🔴 High → 🟡 Medium → 🟢 Low. Внутри одного приоритета сохранен порядок по номерам вопросов.

### Q2.1: E2E тесты - моки провайдеров (Этап 6.3)
**Фаза/Шаг:** Фаза 4, Шаг 4.3  
**Дата создания:** 2025-01-27  
**Приоритет:** 🔴 High

**Контекст:**
LiteLLM работает внутри Docker контейнера и делает HTTP запросы к провайдерам. Как мокать эти запросы?

**Вопрос:**
Как мокать провайдеров для E2E тестов?

**Почему важно:**
Блокирует реализацию полных API тестов с реальными запросами к моделям.

**Варианты решения:**
1. Пропустить моки, тестировать только структуру API (текущий подход)
2. Использовать mock HTTP сервер (нужна настройка)
3. Использовать WireMock в Docker сети
4. Использовать тестовый провайдер LiteLLM (если есть)

**Статус:** ⏳ Ожидает решения

---

### Q2.2: E2E тесты - приоритеты пропущенных проверок (Этап 6.3)
**Фаза/Шаг:** Фаза 4, Шаг 4.3  
**Дата создания:** 2025-01-27  
**Приоритет:** 🟡 Medium

**Контекст:**
Много потенциальных проверок, нужно определить приоритеты.

**Вопрос:**
Какие из пропущенных проверок критичны для E2E тестов?

**Почему важно:**
Много потенциальных проверок, нужно определить приоритеты.

**Варианты решения:**
1. Минимальный набор: PostgreSQL health, Nginx доступность, Virtual Key создание
2. Расширенный набор: все 12 проверок из списка
3. Оставить как есть и добавлять по мере необходимости

**Пропущенные проверки:**
1. PostgreSQL health check
2. Nginx health check
3. Разные resource profiles
4. Разные budget profiles
5. Содержимое конфигурационных файлов
6. Virtual Key создание
7. Изоляция контейнеров
8. Volumes и Network
9. Проверка портов
10. Prisma migrations
11. Логи контейнеров

**Статус:** ⏳ Ожидает решения

---

### Q1.1: Планируются ли дополнительные функции, которые могут повлиять на архитектуру?
**Фаза/Шаг:** Фаза 5, Шаг 5.1  
**Дата создания:** 2025-01-27  
**Приоритет:** 🟢 Low

**Контекст:**
Нужно понимать долгосрочные планы развития проекта для принятия архитектурных решений.

**Вопрос:**
Планируются ли дополнительные функции, которые могут повлиять на архитектуру?

**Почему важно:**
Понимание долгосрочных планов поможет принять правильные архитектурные решения и избежать рефакторинга в будущем.

**Варианты решения:**
1. [TODO: Добавить варианты после уточнения]

**Статус:** ⏳ Ожидает ответа

---

### Q1.2: Нужна ли поддержка других платформ кроме Linux?
**Фаза/Шаг:** Фаза 5, Шаг 5.1  
**Дата создания:** 2025-01-27  
**Приоритет:** 🟢 Low

**Контекст:**
Текущий код ориентирован на Linux, но может потребоваться поддержка других платформ.

**Вопрос:**
Нужна ли поддержка других платформ кроме Linux?

**Почему важно:**
Понимание требований к платформам поможет принять правильные архитектурные решения.

**Варианты решения:**
1. [TODO: Добавить варианты после уточнения]

**Статус:** ⏳ Ожидает ответа

---

### Q2.3: Нужны ли unit тесты для `infrastructure/systemd_service.py` и `infrastructure/openwebui_db.py`?
**Фаза/Шаг:** Фаза 4, Шаг 4.1  
**Дата создания:** 2025-01-27  
**Приоритет:** 🟢 Low

**Контекст:**
Эти модули зависят от внешних систем (systemd, база данных PostgreSQL). Основные модули core/ и infrastructure/ покрыты тестами.

**Вопрос:**
Стоит ли добавлять unit тесты с моками для этих модулей, или они достаточно покрыты integration тестами?

**Почему важно:**
Определить приоритеты тестирования для этих модулей.

**Варианты решения:**
1. Добавить unit тесты с моками
2. Оставить для будущего рассмотрения (текущий подход)

**Статус:** ⏳ Ожидает решения

---

## Отвеченные вопросы (база знаний)

**Индекс по темам:**

- **Архитектура и дизайн:** Q0.2 (BaseService)
- **Тестирование:** Q0.3, Q0.4 (E2E тесты)
- **Инструменты качества кода:** Q0.5, Q0.6, Q0.7 (Black, pre-commit, mypy)
- **Технические решения:** Q0.1 (async/await)

---

### Q0.1: Нужна ли поддержка async/await для операций с Docker API?

**Ответ:** Для текущего проекта **не критично**
**Обоснование:**
- Текущая реализация использует `subprocess.run()` - синхронный API
- Операции с Docker (start, stop, logs) выполняются последовательно, не требуют параллельности
- Async добавит сложности без значительных преимуществ
- Нет требований к параллельным операциям с Docker в текущих задачах

**Альтернативы:**
- **Вариант A**: Оставить синхронный подход ✅ **Выбран** - соответствует текущим требованиям
- **Вариант B**: Переписать на async - отклонен, т.к. нет требований и добавит сложности

**Дата закрытия:** 2025-01-27  
**Применено в:** Changelog запись - Этап 5

---

### Q0.2: BaseService - анализ и план (Этап 9)

**Ответ:** Добавлено в план как Фаза 5, Шаг 5.1 для анализа и реализации  
**Обоснование:**
- Все сервисы имеют общие паттерны (project_root, FileRepository)
- Есть дублирование кода, но не критичное
- Принцип YAGNI - не создавать абстракцию без необходимости
- Требуется анализ - достаточно ли дублирования для создания BaseService

**Анализ общих паттернов:**
- Все сервисы (`StartService`, `SetupService`, `ContinueDevService`) принимают `project_root: Path` в `__init__`
- Все используют `self.project_root = Path(project_root)`
- Все используют `FileRepository(self.project_root)` → `self.file_repo`
- `StartService` и `SetupService` используют `ConfigService(self.project_root)` → `self.config_service`

**Дата закрытия:** 2025-01-27  
**Применено в:** IMPROVEMENT_PLAN.md - Фаза 5, Шаг 5.1

---

### Q0.3: E2E тесты - проверка локально (Этап 6.3)

**Ответ:** E2E тесты запускаются ЛОКАЛЬНО на машине разработчика. Prod сервер используется только для сбора информации (мониторинг, логи, метрики), НЕ для запуска тестов.  
**Обоснование:**
- Базовые тесты проходят успешно
- Тесты выполняются в разумное время (~1-2 минуты на тест)
- Изоляция контейнеров работает правильно через COMPOSE_PROJECT_NAME
- Контейнеры и volumes очищаются после тестов

**Дата закрытия:** 2025-01-27  
**Применено в:** Changelog запись - Этап 6

---

### Q0.4: E2E тесты - детали реализации (Этап 6.3)

**Ответ:**
1. Реальный Docker (не testcontainers)
2. Полный цикл: setup → start → health checks → API тесты → stop
3. API тесты с моками провайдеров (базовая структура готова, требуется уточнение подхода)
4. Изоляция тестов: Использовать отдельные контейнеры для каждого теста
5. Timeout: Использовать 300 секунд (5 минут) как в коде
6. Структура: Создать отдельную директорию `tests/e2e/`

**Обоснование:**
- Реальный Docker обеспечивает проверку полного цикла работы
- Изоляция тестов через COMPOSE_PROJECT_NAME предотвращает конфликты
- Timeout 300 секунд соответствует коду приложения

**Дата закрытия:** 2025-01-27  
**Применено в:** Changelog запись - Этап 6

---

### Q0.5: Какой стиль форматирования предпочтителен? (black, autopep8, yapf)

**Ответ:** **Black** - де-факто стандарт для Python проектов  
**Обоснование:**
- Де-факто стандарт для Python проектов
- Обеспечивает единообразие стиля без споров

**Дата закрытия:** 2025-01-27  
**Применено в:** Changelog запись - Этап 1

---

### Q0.6: Нужны ли pre-commit hooks?

**Ответ:** **Да** - стандартная практика, экономит время на CI/CD  
**Обоснование:**
- Стандартная практика
- Экономит время на CI/CD

**Дата закрытия:** 2025-01-27  
**Применено в:** Changelog запись - Этап 1

---

### Q0.7: Какой уровень строгости mypy? (strict, basic, или custom)

**Ответ:** Начать с **basic** (disallow_untyped_defs = false), постепенно повышать строгость  
**Обоснование:**
- Начать с базовой конфигурации для плавной миграции
- Постепенно повышать строгость по мере исправления ошибок

**Дата закрытия:** 2025-01-27  
**Применено в:** Changelog запись - Этап 1

---

## Типы блокеров

🔍 **Требует уточнения от пользователя** - нужно уточнение контекста или требований  
🏗️ **Архитектурная проблема** - противоречие в дизайне  
🐛 **Обнаружен баг** - технический блокер
📊 **Требования неясны** - нужно уточнение бизнес-логики

---

## 🤖 Instructions for AI agent

**Important:** This section contains instructions for working with this artifact. These instructions are self-sufficient and do not require external prompts or templates.

**Artifact System Overview:**

This artifact is part of a system of 4 required artifacts that work together:

1. **PLAN** (`IMPROVEMENT_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
2. **CHANGELOG** (`IMPROVEMENT_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
3. **QUESTIONS** (`IMPROVEMENT_QUESTIONS.md`) - Knowledge base for doubts and solutions. Contains active questions (blockers) and resolved questions.
4. **SESSION_CONTEXT** (`IMPROVEMENT_SESSION_CONTEXT.md`) - Current work state. Contains temporary notes, intermediate decisions, and active context.

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
1. Start with section "Активные вопросы (требуют ответа)" (Active Questions) to check blockers
2. Questions are sorted by priorities: 🔴 High → 🟡 Medium → 🟢 Low
3. Each question contains: Context, Question, Why important, Solution options, Status
4. Use section "Отвеченные вопросы (база знаний)" (Answered Questions) to search for solutions to similar problems
5. Check "Типы блокеров" (Blocker Types) section to understand question categories

**How to update artifacts (created from this template):**
1. When creating new question → add to "Активные вопросы (требуют ответа)" section:
   - Add question with correct priority (🔴 High, 🟡 Medium, 🟢 Low)
   - Sort by priority: 🔴 → 🟡 → 🟢
   - Use format: `### QX.Y: [Title] (Phase X, Step Y)`
   - Include all required sections (see question structure above)
2. Question format: `QX.Y: [Title] (Phase X, Step Y)`
   - QX.Y: Question number (Phase X, Step Y)
   - Title: Brief descriptive title
3. Required sections for active questions:
   - Phase/Step: Phase X, Step Y
   - Creation Date: YYYY-MM-DD
   - Priority: 🔴 High | 🟡 Medium | 🟢 Low
   - Context: Detailed description of situation
   - Question: Specific question requiring clarification
   - Why important: Explanation of impact
   - Solution options: List of options with pros/cons
   - Status: ⏳ Pending
4. When answering question → move to "Отвеченные вопросы (база знаний)" section:
   - Update status: ⏳ Pending → ✅ Resolved
   - Add answer information:
     - Answer (accepted solution)
     - Rationale (why chosen)
     - Closing Date: YYYY-MM-DD
     - Applied in: CHANGELOG link
   - Move question from "Активные вопросы" to "Отвеченные вопросы"
   - Create CHANGELOG entry about resolution
5. Update question status (⏳ Pending → ✅ Resolved) when answered

**Formatting rules:**
- Use exact question format as defined in question structure above
- Sort questions by priority: 🔴 High → 🟡 Medium → 🟢 Low
- Use consistent date format: YYYY-MM-DD
- Links use `@[ARTIFACT_NAME]` notation
- Status icons: ⏳ Pending, ✅ Resolved

**When to use this file:**
- When discovering blocker or unclear requirements
- When searching for solutions to similar problems
- When checking active questions before starting work
- When making architectural decisions
- When uncertain and might hallucinate an answer (create question instead)

**Related artifacts:**
- `IMPROVEMENT_PLAN.md` - for understanding question context (phase/step)
- `IMPROVEMENT_CHANGELOG.md` - for history of applied solutions
- `IMPROVEMENT_SESSION_CONTEXT.md` - for current session context

**Question Types:**
- 🔍 **Requires user clarification** - needs clarification of context or requirements
- 🏗️ **Architectural problem** - design contradiction
- 🐛 **Bug discovered** - technical blocker
- 📊 **Requirements unclear** - needs clarification of business logic
- 🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation

## 🤖 Instructions for AI agent

**Important:** This section contains instructions for working with this artifact. These instructions are self-sufficient and do not require external prompts or templates.

**Artifact System Overview:**

This artifact is part of a system of 4 required artifacts that work together:

1. **PLAN** (`IMPROVEMENT_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
2. **CHANGELOG** (`IMPROVEMENT_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
3. **QUESTIONS** (`IMPROVEMENT_QUESTIONS.md`) - Knowledge base for doubts and solutions. Contains active questions (blockers) and resolved questions.
4. **SESSION_CONTEXT** (`IMPROVEMENT_SESSION_CONTEXT.md`) - Current work state. Contains temporary notes, intermediate decisions, and active context.

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
1. Start with section "Активные вопросы (требуют ответа)" (Active Questions) to check blockers
2. Questions are sorted by priorities: 🔴 High → 🟡 Medium → 🟢 Low
3. Each question contains: Context, Question, Why important, Solution options, Status
4. Use section "Отвеченные вопросы (база знаний)" (Answered Questions) to search for solutions to similar problems
5. Check "Типы блокеров" (Blocker Types) section to understand question categories

**How to update artifacts (created from this template):**
1. When creating new question → add to "Активные вопросы (требуют ответа)" section:
   - Add question with correct priority (🔴 High, 🟡 Medium, 🟢 Low)
   - Sort by priority: 🔴 → 🟡 → 🟢
   - Use format: `### QX.Y: [Title] (Phase X, Step Y)`
   - Include all required sections (see question structure above)
2. Question format: `QX.Y: [Title] (Phase X, Step Y)`
   - QX.Y: Question number (Phase X, Step Y)
   - Title: Brief descriptive title
3. Required sections for active questions:
   - Phase/Step: Phase X, Step Y
   - Creation Date: YYYY-MM-DD
   - Priority: 🔴 High | 🟡 Medium | 🟢 Low
   - Context: Detailed description of situation
   - Question: Specific question requiring clarification
   - Why important: Explanation of impact
   - Solution options: List of options with pros/cons
   - Status: ⏳ Pending
4. When answering question → move to "Отвеченные вопросы (база знаний)" section:
   - Update status: ⏳ Pending → ✅ Resolved
   - Add answer information:
     - Answer (accepted solution)
     - Rationale (why chosen)
     - Closing Date: YYYY-MM-DD
     - Applied in: CHANGELOG link
   - Move question from "Активные вопросы" to "Отвеченные вопросы"
   - Create CHANGELOG entry about resolution
5. Update question status (⏳ Pending → ✅ Resolved) when answered

**Formatting rules:**
- Use exact question format as defined in question structure above
- Sort questions by priority: 🔴 High → 🟡 Medium → 🟢 Low
- Use consistent date format: YYYY-MM-DD
- Links use `@[ARTIFACT_NAME]` notation
- Status icons: ⏳ Pending, ✅ Resolved

**When to use this file:**
- When discovering blocker or unclear requirements
- When searching for solutions to similar problems
- When checking active questions before starting work
- When making architectural decisions
- When uncertain and might hallucinate an answer (create question instead)

**Related artifacts:**
- `IMPROVEMENT_PLAN.md` - for understanding question context (phase/step)
- `IMPROVEMENT_CHANGELOG.md` - for history of applied solutions
- `IMPROVEMENT_SESSION_CONTEXT.md` - for current session context

**Question Types:**
- 🔍 **Requires user clarification** - needs clarification of context or requirements
- 🏗️ **Architectural problem** - design contradiction
- 🐛 **Bug discovered** - technical blocker
- 📊 **Requirements unclear** - needs clarification of business logic
- 🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation
