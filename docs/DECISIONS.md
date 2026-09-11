# Decisions

## 1. Django + React
**Decision:** Use Django REST Framework for the backend and React/Vite for the UI.  
**Rejected alternative:** Node/Express for this assignment.  
**Reason:** Django is the preferred backend in the brief and keeps the data model, importer, API and tests in one simple project.

## 2. SQLite
**Decision:** Use SQLite for local development.  
**Rejected alternative:** PostgreSQL.  
**Reason:** The assignment data is small and the brief allows SQLite; SQLite keeps setup fast and reproducible.

## 3. Preserve raw CSV values
**Decision:** Store raw string values as well as parsed Decimal values.  
**Rejected alternative:** Rejecting malformed rows during import.  
**Reason:** Dirty rows must survive ingestion and must not be silently dropped.

## 4. Normalize System B references
**Decision:** Remove non-alphanumeric characters and lowercase references.  
**Rejected alternative:** Exact string matching.  
**Reason:** System B contains formatting differences such as `REC-1034`, `rec1034` and `REC - 1070`.

## 5. Explicit tenant context
**Decision:** The disagreements API requires `org_id`, and comparison queries are restricted to locations belonging to that organization.  
**Rejected alternative:** Loading all organizations and filtering only in React.  
**Reason:** Tenant isolation must be enforced server-side.

## 6. Duplicate is a primary reason
**Decision:** A reference with multiple B entries is reported as `Duplicate in B`; value comparison is skipped for that reference.  
**Rejected alternative:** Reporting the same duplicate entries again as value mismatches.  
**Reason:** This avoids double-counting the same underlying data-quality problem and makes the reason filter deterministic.

## 7. Show every duplicate row
**Decision:** Each B entry involved in a duplicate is displayed.  
**Rejected alternative:** Showing only one aggregate duplicate row.  
**Reason:** The user needs to see both conflicting/duplicated entries and their values.
