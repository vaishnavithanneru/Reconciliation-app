# System Reconciliation

A small full-stack reconciliation application for comparing records from System A and System B.

## What is built

- CSV ingestion for:
  - `locations.csv`
  - `system_a.csv`
  - `system_b.csv`
- Django + Django REST Framework backend.
- SQLite database.
- Raw CSV values are preserved alongside parsed numeric values.
- System B record references are normalized before comparison.
- Four disagreement categories:
  - Missing in B
  - Orphan in B
  - Duplicate in B
  - Value mismatch
- Server-side organization/tenant filtering.
- React UI with:
  - organization selector
  - reason filter
  - value sorting
  - disagreement table
- Automated tests for:
  - missing in B
  - orphan in B
  - duplicate in B
  - value mismatch
  - tenant isolation

## Project structure

```text
reconciliation_app/
├── backend/
├── frontend/
├── data/
├── docs/
└── README.md
```

## Requirements

- Python 3.10+
- Node.js 18+

## Backend setup

Open Terminal:

```bash
cd reconciliation_app/backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py import_data

python manage.py test
```

Start Django:

```bash
python manage.py runserver
```

Backend runs at:

```text
http://127.0.0.1:8000
```

## Frontend setup

Open a second Terminal:

```bash
cd reconciliation_app/frontend

npm install
npm run dev
```

Open the URL printed by Vite, normally:

```text
http://localhost:5173
```

## API

Organizations:

```text
GET /api/organizations/
```

Disagreements:

```text
GET /api/disagreements/?org_id=ORG-A
```

Optional reason:

```text
GET /api/disagreements/?org_id=ORG-A&reason=value_mismatch
```

Optional sort:

```text
GET /api/disagreements/?org_id=ORG-A&sort=value_asc
```

## Import behavior

The importer does not discard malformed numeric values.

For example, a value such as:

```text
1,25,400.00
```

is normalized to a Decimal value of:

```text
125400.00
```

Blank numeric values remain stored as raw blank strings with a null parsed value.

Every CSV row receives a source row number. Raw values are kept so the original dirty input can be inspected.

## Tenant isolation

The API requires an `org_id`.

The comparator first finds locations belonging to that organization and only loads records whose location belongs to that organization.

The React application never receives another organization's disagreement rows.

This is intentionally enforced in the backend rather than relying on frontend filtering.

## What is deliberately not built

- Authentication/authorization.
- Production deployment configuration.
- Background import jobs.
- Pagination.
- Advanced visual design.
- Editing source data.
- Automatic conflict resolution.
- Complex fuzzy matching.

These were deliberately left out because the assignment prioritizes a small, correct reconciliation slice.

## How I worked with the agent

I used an AI coding agent as an implementation assistant. I first converted the assignment into a small flow:

```text
CSV -> import -> database -> normalization -> comparison -> tenant filter -> API -> React
```

I then checked the real CSV columns and dirty records before implementing the comparison logic. The agent was used for scaffolding, repetitive code and test structure, while the discrepancy rules and tenant-isolation behavior were reviewed against the assignment requirements and sample data.

## One thing the AI agent got wrong

The initial implementation direction risked treating all record references as equivalent after stripping punctuation. I checked the real data and noticed that a digits-only reference such as `1112` should not automatically become `REC-1112` because that would invent information that is not present in the source. The final normalizer only removes formatting characters and does not invent a prefix.

## Least confident part

The least confident part is the exact intended business interpretation of duplicate rows when their values also differ. I chose `Duplicate in B` as the primary reason and show every duplicate B entry, while skipping a second value-mismatch classification for those duplicate references. This keeps each underlying reference from being double-counted.

## If I had a second day

I would first add stronger ingestion diagnostics and a dedicated import report showing every malformed/blank field, then add API-level tenant-isolation tests and edge-case tests around reference normalization and numeric formats.

## Test command

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

The test suite covers the four required disagreement types plus tenant isolation.
