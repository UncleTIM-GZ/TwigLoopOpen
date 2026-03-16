# Platform Rules Overview

## Project Types

| Type | Who | Review | Work Units |
|------|-----|--------|-----------|
| General | Anyone with founder role | Standard | EWU only |
| Public Benefit | Organizations, help seekers | Mandatory human review | EWU + SWU (if sponsored) |
| Recruitment | Contributors seeking talent | Standard | EWU + RWU |

## Project Lifecycle

```
draft → published → open → in_progress → completed
                                        → closed
```

Public benefit projects require `reviewer_required → human_review_passed` before advancing.

## Task Lifecycle

```
draft → assigned → in_progress → submitted → completed
                                            → closed
```

## Quotas (v1)

| Rule | Limit |
|------|-------|
| Work packages per project | 5 |
| Tasks per work package | 6 |
| Tasks per project | 20 |
| EWU per task | 8 |
| Active projects per new founder | 2 |
| Open seats per founder | 12 |
| Active tasks per founder | 30 |

## Preflight Validation

Before a project is published, the platform validates all quota rules. This catches issues early — before data is committed.

Quotas are also enforced at CRUD time as a second layer of protection.

## Work Units

See [EWU/RWU/SWU Rules](../ewu-rwu-swu-rules.md) for the complete specification.

Summary:
- **EWU** = base_weight(task_type) × avg(complexity, criticality, collaboration) × risk_multiplier
- **RWU** = EWU × 1.2 (recruitment projects only)
- **SWU** = EWU × 1.0 (sponsored public-benefit projects)
