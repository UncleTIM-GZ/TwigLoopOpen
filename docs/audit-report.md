# Audit Report — feat/freeze-regression-p1-closures

**Date:** 2026-03-15
**Branch:** `feat/freeze-regression-p1-closures`
**Scope:** 18 modified files, 10 new files
**Reviewers:** Software Architect, Kieran Python Reviewer, Schema Drift Detector, Security Sentinel

---

## Summary

| Severity | Count |
|----------|-------|
| HIGH     | 9     |
| MEDIUM   | 12    |
| LOW      | 8     |

### Cross-Agent Consensus (issues found by 3+ agents)

| Issue | Agents |
|-------|--------|
| Silent exception swallowing (no logging) | 4/4 |
| `list_seats` missing authentication | 3/4 |
| Route path collision `/credentials/verify/{vc_id}` unreachable | 3/4 |
| `credential_type` missing `Literal` constraint | 3/4 |
| Missing NATS credential event subjects | 3/4 |
| `me.py` Router→Service→Repository layering violation | 2/4 |

---

## HIGH Severity

### H-1: Task Card Update Bypasses State Machine (CRITICAL)

**Category:** Security / Business Logic
**File:** `apps/core-api/app/services/task_card_service.py:82-95`
**Source:** Security Sentinel

**Issue:** `UpdateTaskCardRequest` includes a `status` field. In `TaskCardService.update()`, all fields from `req.model_dump(exclude_unset=True)` are passed directly to `update_fields()` **without whitelist filtering**. A caller can `PATCH /tasks/{task_id}` with `{"status": "completed"}`, completely bypassing `validate_task_transition()` which is only enforced in `transition_status()`.

**Impact:** State machine bypass. Attacker can jump tasks to `"completed"` without review, enabling fraudulent credential issuance for unreviewed work. This is the most severe finding.

**Recommendation:** Remove `status` from `UpdateTaskCardRequest`, or add whitelist filtering (like `me.py:85-89`).

---

### H-2: Route Path Collision — `/credentials/verify/{vc_id}` Is Unreachable

**Category:** Architecture / Bug
**File:** `apps/core-api/app/api/v1/credentials.py:32-50`
**Source:** Python Reviewer, Schema Drift Detector

**Issue:** `GET /{vc_id}` (line 32) is defined before `GET /verify/{vc_id}` (line 43). FastAPI matches routes in definition order. A request to `/credentials/verify/<uuid>` will match `/{vc_id}` first with `vc_id="verify"`, which fails with 422 because `"verify"` is not a valid UUID. The verify endpoint is **completely unreachable**.

**Recommendation:** Reorder routes (put `/verify/{vc_id}` before `/{vc_id}`), or restructure to `/{vc_id}/verify`.

---

### H-3: `verify_credential` Endpoint Has No Authentication

**Category:** Security
**File:** `apps/core-api/app/api/v1/credentials.py:43-50`
**Source:** Security Sentinel, Architect

**Issue:** `GET /credentials/verify/{vc_id}` has no `get_current_user` dependency — fully public. Returns full `CredentialResponse` with `actor_id`, `project_id`, `task_id`, and `credential_data` JSON.

**Impact:** Information disclosure. An attacker can enumerate credential UUIDs to map actor-project relationships.

**Recommendation:** Add auth, or strip response to `{valid: bool}` only.

---

### H-4: `list_seats` Endpoint Has No Authentication

**Category:** Security
**File:** `apps/core-api/app/api/v1/applications.py:70-77`
**Source:** Security Sentinel, Architect, Schema Drift Detector

**Issue:** `GET /projects/{project_id}/seats` requires no auth. Leaks `actor_id`, `seat_type`, `role_needed`, `status`, `reward_enabled` for all team members.

**Recommendation:** Add `Depends(get_current_user)`. Restrict to project founder and seat holders.

---

### H-5: Silent Exception Swallowing in Event Recording

**Category:** Reliability / Observability
**Files:**
- `apps/core-api/app/services/vc_service.py:60`
- `apps/core-api/app/services/task_card_service.py:65,125`
- `apps/core-api/app/services/application_service.py:82,172,211`
**Source:** All 4 agents

**Issue:** `contextlib.suppress(Exception)` and `except Exception: pass` swallow ALL exceptions including programming bugs (`RuntimeError`, `TypeError`), not just transient I/O failures. Zero logging means zero observability in production.

**Recommendation:** Add `logger.exception("Failed to record domain event")` at WARNING level. Narrow catch to `SQLAlchemyError | OSError`.

---

### H-6: Missing CORS Configuration

**Category:** Security
**File:** `apps/core-api/app/main.py`
**Source:** Security Sentinel

**Issue:** No `CORSMiddleware` configured. Without explicit CORS restrictions, any malicious website can make authenticated API calls using the user's JWT.

**Recommendation:** Add `CORSMiddleware` with explicit `allow_origins` restricted to frontend domain(s).

---

### H-7: No `credential_type` Enum Validation at Schema Level

**Category:** Security / Data Integrity
**File:** `apps/core-api/app/schemas/credential.py:12`
**Source:** Python Reviewer, Architect, Schema Drift Detector

**Issue:** `credential_type: str` with no Pydantic constraint. Invalid types pass schema validation and only fail at service layer with `ConflictError` (409) instead of proper 422.

**Recommendation:** `credential_type: Literal["task_completion", "project_participation"]`

---

### H-8: Missing NATS Event Subjects for Credential Operations

**Category:** Architecture
**File:** `packages/shared-events/src/shared_events/subjects.py`
**Source:** Architect, Schema Drift Detector, Security Sentinel

**Issue:** No `CREDENTIAL_ISSUED` subject in `Subjects`. VC service records domain events via `EventWriteService` but does NOT publish to NATS JetStream. Breaks architecture invariant that all inter-service events go through NATS.

**Recommendation:** Add credential subjects and publish via `publish_event()`.

---

### H-9: `me.py` Router Layer Directly Operates Repository — Skips Service Layer

**Category:** Architecture
**File:** `apps/core-api/app/api/v1/me.py:47-92`
**Source:** Architect

**Issue:** `get_me` and `update_me` directly instantiate `AccountRepository`/`ActorRepository` and execute business logic (whitelist filtering, field mapping) in the Router layer. Violates the established Router→Service→Repository pattern used by all other endpoints.

**Impact:** Logic cannot be reused or independently tested. If profile updates need events/audit in the future, logic is scattered.

**Recommendation:** Extract to a `ProfileService` class following existing patterns.

---

## MEDIUM Severity

### M-1: Application State Machine Bypass

**Category:** Data Integrity
**File:** `apps/core-api/app/services/application_service.py:104-118`
**Source:** Architect, Security Sentinel

**Issue:** `review()` sets `req.decision` directly as status without state machine validation. Only a hardcoded guard `("submitted", "under_review")` exists, but `decision` values (`"accepted"`, `"rejected"`, `"converted_to_growth_seat"`) are not modeled in a state machine like tasks/projects.

---

### M-2: Profile Page — React Hooks Violation

**Category:** Bug (React)
**File:** `apps/web/src/app/dashboard/profile/page.tsx:82`
**Source:** Architect, Python Reviewer

**Issue:** `useUpdateProfile()` called after conditional returns. Violates Rules of Hooks — will cause "Rendered fewer hooks than expected" runtime error.

**Fix:** Move hook call above all conditional returns.

---

### M-3: `preferredRoles` and `externalLinks` — Dead Form Fields

**Category:** UX
**File:** `apps/web/src/app/dashboard/profile/page.tsx:31-32,95-102`
**Source:** Architect

**Issue:** Form collects data but `handleSubmit` discards it. Backend schema has no support for these fields either.

---

### M-4: `structural_cluster_id` Type Mismatch (Model vs Migration)

**Category:** Schema Drift
**Files:**
- Model: `apps/core-api/app/models/project.py:46-48` → `UUID(as_uuid=True)`
- Migration: `alembic/versions/a002_...:52` → `sa.String(length=64)`
**Source:** Schema Drift Detector

**Issue:** Model declares UUID, migration creates VARCHAR(64). Pre-existing from `main` but affects this branch.

---

### M-5: Numeric Precision/Scale Mismatches (6 columns)

**Category:** Schema Drift
**Source:** Schema Drift Detector

| Column | Model | Migration |
|--------|-------|-----------|
| `actors.completion_rate` | `Numeric(10,2)` | `Numeric(6,4)` |
| `actors.coordination_load_score` | `Numeric(10,2)` | `Numeric(10,4)` |
| `projects.dependency_density` | `Numeric(10,2)` | `Numeric(10,4)` |
| `projects.role_diversity_score` | `Numeric(10,2)` | `Numeric(10,4)` |
| `projects.project_complexity_score` | `Numeric(10,2)` | `Numeric(10,4)` |
| `work_packages.dependency_density` | `Numeric(10,2)` | `Numeric(10,4)` |

**Impact:** ORM believes scale=2, DB stores scale=4. Subtle precision bugs possible.

---

### M-6: String Length Mismatches (Model > DB)

**Category:** Schema Drift
**Source:** Schema Drift Detector

| Column | Model | DB |
|--------|-------|----|
| `application_source` | `String(50)` | `String(32)` |
| `decision_reason_code` | `String(100)` | `String(64)` |

**Impact:** Strings between 33-50 / 65-100 chars will cause DB-level `value too long` errors.

---

### M-7: Duplicate Project Lookup in `vc_service.issue()`

**Category:** Performance
**File:** `apps/core-api/app/services/vc_service.py:40-43,107`
**Source:** Architect, Python Reviewer

---

### M-8: No Pagination on List Endpoints

**Category:** Performance
**Files:** `me.py:95-102` (credentials), `applications.py:36-44`, `applications.py:70-77` (seats)
**Source:** Security Sentinel

---

### M-9: `vc_repo.update_status()` Mutates Object + Dead Code

**Category:** Code Quality
**File:** `apps/core-api/app/repositories/vc_repo.py:34-40`
**Source:** Python Reviewer

**Issue:** Directly mutates `vc.status = status` (violates immutability convention). Also never called anywhere — dead code.

---

### M-10: VC Unit Tests — Minimal Coverage

**Category:** Testing
**File:** `tests/unit/test_vc_service.py`
**Source:** Architect, Python Reviewer

**Issue:** Only 4 trivial tests. No coverage for authorization, credential data building, or error paths. Well below 80% minimum.

---

### M-11: Credential Issuance Lacks Duplicate Prevention

**Category:** Data Integrity
**File:** `apps/core-api/app/services/vc_service.py:32-69`
**Source:** Security Sentinel

**Issue:** No check for existing credential with same `(actor_id, project_id, task_id, credential_type)`. Unlimited duplicates possible.

---

### M-12: `useUpdateProfile` Uses `unknown` Response Type

**Category:** Code Quality (TypeScript)
**File:** `apps/web/src/hooks/use-auth.ts:77`

---

## LOW Severity

### L-1: JWT Stored in localStorage (XSS Risk)

**File:** `apps/web/src/lib/auth.ts:14-17`
**Source:** Security Sentinel. Acceptable for MVP but should move to httpOnly cookies.

### L-2: `rwu_swu.py` — No Negative EWU Validation

**File:** `apps/core-api/app/domain/rwu_swu.py:40-48`

### L-3: `UpdateProfileRequest` — No String Length Limits

**File:** `apps/core-api/app/schemas/user.py:34-62`. `display_name`, `bio`, `availability` accept unlimited-length strings.

### L-4: Profile Page — `skills`/`interestedTypes` Not Back-Filled from API

**File:** `apps/web/src/app/dashboard/profile/page.tsx:41-46`. Only `displayName`, `bio`, `availability` are initialized from actor data.

### L-5: Error Messages Leak State Machine Details

**File:** `apps/core-api/app/domain/state_machine.py:40-42,50-52`. Error response includes full list of allowed transitions.

### L-6: `_to_response` Static Methods Repeated Across Services

**Files:** `application_service.py:220-234`, `vc_service.py:129-141`, `task_card_service.py:155-175`. Consider `@classmethod` factories on response schemas.

### L-7: No Rate Limiting on Any Endpoint

**Source:** Security Sentinel. Especially needed on auth, credential issuance, and application submission.

### L-8: `# type: ignore[untyped-decorator]` on All Route Decorators

**Files:** All router files. Should be resolved at mypy config level.

---

## Schema Drift Summary

| Check | Status | Notes |
|-------|--------|-------|
| `verifiable_credentials` table migration | OK | `a001_add_missing_base_tables.py` |
| Model ↔ Schema field alignment (VC) | OK | `CredentialResponse` maps correctly |
| `rwu`/`swu` on `task_cards` | OK | `Numeric(10,2)`, nullable |
| `structural_cluster_id` type | **DRIFT** | Model=UUID, Migration=String(64) |
| Numeric precision (6 columns) | **DRIFT** | Model scale=2, DB scale=4 |
| String lengths (2 columns) | **DRIFT** | Model > DB max length |
| NATS subject naming | **MISSING** | No credential events |
| Status enum DB constraints | **NONE** | All `String(50)`, no CHECK |

---

## Architecture Invariant Check

| Invariant | Status |
|-----------|--------|
| core-api is only DB write path from web | PASS |
| ai-assist-service never writes main DB | PASS |
| source-sync-worker decoupled from core-api | PASS |
| Account vs Actor separation | PASS |
| Router → Service → Repository layering | **FAIL** (`me.py` H-9) |
| NATS `domain.entity.action` naming | PASS |
| Temporal for durable workflows only | PASS |
| State machine enforced on all transitions | **FAIL** (H-1 task bypass, M-1 application) |

---

## Remediation Priority

### Immediate (before merge)
1. **H-1** Task card update state machine bypass — remove `status` from `UpdateTaskCardRequest`
2. **H-2** Route path collision — reorder `/verify/{vc_id}` before `/{vc_id}`
3. **H-3** Unauthenticated verify endpoint — add auth or strip response
4. **H-4** Unauthenticated seats endpoint — add `get_current_user`
5. **H-7** `credential_type` → `Literal` type
6. **M-2** React hooks violation — move hook above conditional returns

### Before release
7. **H-5** Replace silent exception swallowing with logging
8. **H-6** Add CORS middleware
9. **H-8** Add credential NATS subjects
10. **H-9** Extract `ProfileService` from `me.py`
11. **M-1** Application state machine validation

### Next sprint
12. **M-4/M-5/M-6** Schema drift fixes (migration corrections)
13. **M-10** VC test coverage
14. **M-11** Credential deduplication
15. **M-8** Add pagination to list endpoints

---

## Positive Observations

1. **Type hints complete** — modern Python 3.10+ syntax (`str | None`, `list[str]`) throughout
2. **`rwu_swu.py` well-structured** — mirrors `ewu.py`, uses `Decimal` for financial precision, excellent unit tests
3. **State machine regression tests excellent** — exhaustive coverage of valid/invalid transitions
4. **Withdrawal flow** follows established patterns perfectly
5. **`UpdateProfileRequest`** uses `extra = "forbid"` and field validators — good defensive practice
6. **Import organization clean** — consistent stdlib/third-party/local grouping
