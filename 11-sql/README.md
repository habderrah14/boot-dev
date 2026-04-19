# Module 11 — Learn SQL

> SQL is 50 years old and will outlive everything in your current stack. Knowing it deeply is the single most durable skill a backend developer can invest in.

## Map to Boot.dev

Parallels Boot.dev's **"Learn SQL"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Design a small relational schema with primary keys, foreign keys, and sensible types.
- Perform all CRUD operations in SQL.
- Write SELECTs with filtering, ordering, grouping, aggregations, and subqueries.
- Explain the first three normal forms and when to deliberately denormalize.
- Join tables (INNER, LEFT, RIGHT, FULL) and predict the row count.
- Read an EXPLAIN plan and add the right index.

## Prerequisites

- Comfort with the terminal (Module 02).
- Any SQL database: PostgreSQL 16+ is recommended.

## Chapter index

1. [Introduction](01-introduction.md)
2. [Tables](02-tables.md)
3. [Constraints](03-constraints.md)
4. [CRUD](04-crud.md)
5. [Basic Queries](05-basic-queries.md)
6. [Structuring](06-structuring.md)
7. [Aggregations](07-aggregations.md)
8. [Subqueries](08-subqueries.md)
9. [Normalization](09-normalization.md)
10. [Joins](10-joins.md)
11. [Performance](11-performance.md)

## How this module connects

- HTTP servers (Module 12) almost always talk to SQL for persistence.
- Indexing is a direct application of hashmap and B-tree concepts from Module 06.

## Companion artifacts

- Exercises:
  - [01 — Introduction](exercises/01-introduction-exercises.md)
  - [02 — Tables](exercises/02-tables-exercises.md)
  - [03 — Constraints](exercises/03-constraints-exercises.md)
  - [04 — CRUD](exercises/04-crud-exercises.md)
  - [05 — Basic Queries](exercises/05-basic-queries-exercises.md)
  - [06 — Structuring](exercises/06-structuring-exercises.md)
  - [07 — Aggregations](exercises/07-aggregations-exercises.md)
  - [08 — Subqueries](exercises/08-subqueries-exercises.md)
  - [09 — Normalization](exercises/09-normalization-exercises.md)
  - [10 — Joins](exercises/10-joins-exercises.md)
  - [11 — Performance](exercises/11-performance-exercises.md)
- Extended assessment artifacts:
  - [12 — Debugging Incident Lab](exercises/12-debugging-incident-lab.md)
  - [13 — Code Review Task](exercises/13-code-review-task.md)
  - [14 — System Design Prompt](exercises/14-system-design-prompt.md)
  - [15 — Interview Challenges](exercises/15-interview-challenges.md)
- Solutions:
  - [01 — Introduction](solutions/01-introduction-solutions.md)
  - [02 — Tables](solutions/02-tables-solutions.md)
  - [03 — Constraints](solutions/03-constraints-solutions.md)
  - [04 — CRUD](solutions/04-crud-solutions.md)
  - [05 — Basic Queries](solutions/05-basic-queries-solutions.md)
  - [06 — Structuring](solutions/06-structuring-solutions.md)
  - [07 — Aggregations](solutions/07-aggregations-solutions.md)
  - [08 — Subqueries](solutions/08-subqueries-solutions.md)
  - [09 — Normalization](solutions/09-normalization-solutions.md)
  - [10 — Joins](solutions/10-joins-solutions.md)
  - [11 — Performance](solutions/11-performance-solutions.md)
- Mini-project briefs:
  - [01 — Introduction (Core chapter project)](mini-projects/01-introduction-project.md)
  - [01 — Library Database (Bonus project)](mini-projects/01-library-database.md)
  - [02 — Tables](mini-projects/02-tables-project.md)
  - [03 — Constraints](mini-projects/03-constraints-project.md)
  - [04 — CRUD](mini-projects/04-crud-project.md)
  - [05 — Basic Queries](mini-projects/05-basic-queries-project.md)
  - [06 — Structuring](mini-projects/06-structuring-project.md)
  - [07 — Aggregations](mini-projects/07-aggregations-project.md)
  - [08 — Subqueries](mini-projects/08-subqueries-project.md)
  - [09 — Normalization](mini-projects/09-normalization-project.md)
  - [10 — Joins](mini-projects/10-joins-project.md)
  - [11 — Performance](mini-projects/11-performance-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Introduction.** 1) b, 2) c, 3) b, 4) b, 5) b.
  - 6.  `FLOAT` cannot represent many decimal fractions exactly, so rounding errors accumulate; `NUMERIC` or integer cents keep money exact.
  - 7.  PostgreSQL is stricter than MySQL or SQLite, so it catches bad data and schema mistakes earlier.
- **Ch. 02 — Tables.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. JSONB fits truly sparse or semi-structured attributes better than many nullable columns.
  - 7. Surrogate keys are stable and avoid cascading key-change problems.
- **Ch. 03 — Constraints.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6. Overly aggressive cascades can silently destroy dependent business data.
  - 7. Named constraints produce clearer operational and migration diagnostics.
- **Ch. 04 — CRUD.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6. Transactions prevent partial commits from leaving inconsistent state.
  - 7. `RETURNING` avoids race-prone extra reads after mutation.
- **Ch. 05 — Basic Queries.** 1) b, 2) b, 3) b, 4) b, 5) a.
  - 6. Cursor pagination seeks efficiently and remains stable under inserts.
  - 7. `SELECT *` is acceptable for ad-hoc exploration, not production app paths.
- **Ch. 06 — Structuring.** 1) b, 2) a, 3) b, 4) b, 5) a.
  - 6. CTEs improve readability and reuse for multi-step query logic.
  - 7. Materialized views trade freshness for significantly faster reads.
- **Ch. 07 — Aggregations.** 1) b, 2) b, 3) b, 4) a, 5) b.
  - 6. Window functions preserve row detail while computing group-level metrics.
  - 7. Multiple OVER sorts can dominate runtime without careful planning.
- **Ch. 08 — Subqueries.** 1) b, 2) a, 3) d, 4) c, 5) b.
  - 6. EXISTS can short-circuit and handles NULL edge cases better than NOT IN.
  - 7. LATERAL enables per-row dependent subqueries like top-N per group.
- **Ch. 09 — Normalization.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6. 3NF solves most practical anomaly classes; higher forms are rarer in typical systems.
  - 7. Denormalized projections need deterministic sync (triggers/jobs/CDC).
- **Ch. 10 — Joins.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. NATURAL JOIN is fragile because shared-column changes silently alter join logic.
  - 7. FULL OUTER JOIN highlights mismatches across two datasets/sources.
- **Ch. 11 — Performance.** 1) d, 2) b, 3) b, 4) b, 5) b.
  - 6. Functional predicates require matching functional indexes to stay indexable.
  - 7. Extra indexes speed reads but slow writes and consume storage.
