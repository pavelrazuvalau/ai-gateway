# Knowledge Base Section Priorities for Sorting

> **Purpose**: Определение приоритетов секций KB для последующей сортировки
> **Related**: [PROMPT_ENGINEERING_KNOWLEDGE_BASE.md](./PROMPT_ENGINEERING_KNOWLEDGE_BASE.md)

---

## Priority Levels

| Priority | Name | Description | Reading Order |
|----------|------|-------------|---------------|
| **P1** | Foundational | Фундамент для понимания KB | Читается первым |
| **P2** | Core Content | Ключевой практический контент | Основное чтение |
| **P3** | Practical Applications | Практические применения | По необходимости |
| **P4** | Reference/Advanced | Справочная информация | При углублении |
| **P5** | Meta/Support | Мета-информация о KB | Для контрибьюторов |

---

## Prioritization Criteria

1. **Зависимость других секций** — секции, от которых зависят другие, получают более высокий приоритет
2. **Частота использования** — чаще используемые секции выше
3. **Критичность для качества** — влияние на качество промптов
4. **Порядок чтения** — логический порядок освоения материала
5. **Соответствие Categories Map** — группировка по категориям из KB

---

## Complete Section Priority Table

| Current # | Section | Priority | Category (from Map) | Rationale |
|-----------|---------|----------|---------------------|-----------|
| 1 | Definitions | **P1** | — | Фундаментальные концепции KB |
| 2 | Where to Add New Information | **P5** | — | Мета: для контрибьюторов |
| 3 | Template for New Sections | **P5** | — | Мета: шаблон для новых секций |
| 4 | Knowledge Base Categories Map | **P1** | — | Структурная карта KB |
| 5 | Criteria for Adding Information | **P5** | — | Мета: критерии добавления |
| 6 | Glossary of Terms | **P1** | — | Единая терминология |
| 7 | Style Guide for System Prompts | **P1** | STYLE AND FORMATTING | Базовые принципы написания |
| 8 | Top-10 Common Mistakes | **P2** | MISTAKES | Критические ошибки |
| 9 | Best Practices | **P2** | BEST PRACTICES | Основные рекомендации |
| 10 | Prompt Engineering Techniques | **P2** | TECHNIQUES | Ключевые техники |
| 11 | Prompt Security | **P2** | SECURITY | Критично для production |
| 12 | Structured Output | **P3** | STRUCTURED OUTPUT | Важно для интеграций |
| 13 | Anti-patterns | **P2** | MISTAKES | Что НЕ делать |
| 14 | Conditional Logic in Prompts | **P3** | TECHNIQUES | Практические паттерны |
| 15 | Model Optimization | **P4** | — | Технические детали |
| 16 | Instruction Duplication | **P4** | — | Когда дублировать |
| 17 | Working with Templates | **P3** | TEMPLATES | Работа с шаблонами |
| 18 | Conclusions and Recommendations | **P5** | — | Мета: резюме |
| 19 | File Operation Practices | **P3** | FILE OPERATIONS | Стратегии для файлов |
| 20 | When to Stop: Avoiding Over-optimization | **P3** | BEST PRACTICES | "Good Enough" принцип |
| 21 | Example Redundancy for Modern Models | **P4** | — | Избыточность примеров |
| 22 | Sufficient Quality Gateway | **P3** | BEST PRACTICES | Checkpoint качества |
| 23 | Production Code Quality and Refactoring | **P4** | BEST PRACTICES | Критерии качества кода |
| 24 | Guard Rails for Vibe Coding | **P3** | BEST PRACTICES | Guard rails для кодинга |
| 25 | Guard Rails for Planning | **P3** | BEST PRACTICES | Guard rails для планирования |
| 26 | Role Definition in System Prompts | **P4** | STYLE AND FORMATTING | Структура ролей |
| 27 | Agent-Agnostic Knowledge Base | **P4** | — | Универсальные инструменты |
| 28 | Knowledge Base as Database | **P4** | — | Стратегии поиска |
| 29 | Structuring Reference Files | **P4** | — | Структурирование файлов |
| 30 | Adaptive Plan Updates | **P4** | BEST PRACTICES | Обновление планов |
| 31 | Agent Loop Patterns | **P4** | — | Паттерны циклов |
| 32 | System Prompt Consistency Checklist | **P4** | STYLE AND FORMATTING | Чеклист консистентности |
| 33 | Interactive Questions with Recommendations | **P4** | BEST PRACTICES | Формат вопросов |
| 34 | Sources | **P5** | SOURCES | Внешние источники |

---

## Recommended Sort Order

### New Table of Contents (sorted by priority)

```
## Table of Contents

### P1 — Foundational (Читать первым)
1. [Definitions](#definitions)
2. [Glossary of Terms](#glossary-of-terms)
3. [Knowledge Base Categories Map](#knowledge-base-categories-map)
4. [Style Guide for System Prompts](#style-guide-for-system-prompts)

### P2 — Core Content (Ключевой контент)
5. [Top-10 Common Mistakes](#top-10-common-mistakes)
6. [Best Practices](#best-practices)
7. [Prompt Engineering Techniques](#prompt-engineering-techniques)
8. [Prompt Security](#prompt-security)
9. [Anti-patterns](#anti-patterns)

### P3 — Practical Applications (Практические применения)
10. [Structured Output](#structured-output)
11. [Conditional Logic in Prompts](#conditional-logic-in-prompts)
12. [Working with Templates](#working-with-templates)
13. [File Operation Practices](#file-operation-practices)
14. [When to Stop: Avoiding Over-optimization](#when-to-stop-avoiding-over-optimization)
15. [Sufficient Quality Gateway](#sufficient-quality-gateway)
16. [Guard Rails for Planning](#guard-rails-for-planning)
17. [Guard Rails for Vibe Coding on Large Projects](#guard-rails-for-vibe-coding-on-large-projects)

### P4 — Reference/Advanced (Справочная информация)
18. [Model Optimization](#model-optimization)
19. [Instruction Duplication](#instruction-duplication)
20. [Example Redundancy for Modern Models](#example-redundancy-for-modern-models)
21. [Production Code Quality and Refactoring Criteria](#production-code-quality-and-refactoring-criteria)
22. [Role Definition in System Prompts](#role-definition-in-system-prompts-structure-and-components)
23. [Agent-Agnostic Knowledge Base and Coding Agent Tools](#agent-agnostic-knowledge-base-and-coding-agent-tools)
24. [Knowledge Base as Database](#knowledge-base-as-database-search-and-retrieval-strategy)
25. [Structuring Reference Files](#structuring-reference-files-for-efficient-agent-instruction-search)
26. [Adaptive Plan Updates](#adaptive-plan-updates)
27. [Agent Loop Patterns](#agent-loop-patterns)
28. [System Prompt Consistency Checklist](#system-prompt-consistency-checklist)
29. [Interactive Questions with Recommendations](#interactive-questions-with-recommendations)

### P5 — Meta/Support (Мета-информация)
30. [Where to Add New Information](#where-to-add-new-information-for-ai-agents)
31. [Template for New Sections](#template-for-new-sections)
32. [Criteria for Adding Information](#criteria-for-adding-information-to-knowledge-base)
33. [Conclusions and Recommendations](#conclusions-and-recommendations-for-ai-agents)
34. [Sources](#sources)
```

---

## Priority Distribution Summary

| Priority | Count | Percentage |
|----------|-------|------------|
| P1 | 4 | 12% |
| P2 | 5 | 15% |
| P3 | 8 | 23% |
| P4 | 12 | 35% |
| P5 | 5 | 15% |
| **Total** | **34** | **100%** |

---

## Alignment with Categories Map

Current Categories Map vs Priorities:

| Category | Sections | Priority Range |
|----------|----------|----------------|
| STYLE AND FORMATTING | Style Guide, Role Definition, Consistency Checklist | P1, P4, P4 |
| MISTAKES | Top-10 Mistakes, Anti-patterns | P2, P2 |
| BEST PRACTICES | Best Practices, When to Stop, Quality Gateway, Guard Rails, etc. | P2-P4 |
| TECHNIQUES | Prompt Engineering Techniques, Conditional Logic | P2, P3 |
| SECURITY | Prompt Security | P2 |
| STRUCTURED OUTPUT | Structured Output | P3 |
| FILE OPERATIONS | File Operation Practices | P3 |
| TEMPLATES | Working with Templates | P3 |
| SOURCES | Sources | P5 |

---

## Notes for Sorting Implementation

1. **P1 секции должны идти в начале** — это фундамент понимания
2. **Glossary лучше разместить ПЕРЕД Style Guide** — термины нужны для понимания стиля
3. **Categories Map можно оставить после Glossary** — показывает структуру после терминологии
4. **P5 секции в конце** — мета-информация для контрибьюторов и источники
5. **Sources всегда последняя** — стандартная практика для документации

---

*Created: December 2025*
*For use with: PROMPT_ENGINEERING_KNOWLEDGE_BASE.md v1.1*
