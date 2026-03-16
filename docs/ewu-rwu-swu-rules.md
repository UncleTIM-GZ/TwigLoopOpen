# EWU / RWU / SWU 工作量单位规则文档

**版本:** v1 (2026-03-15)
**状态:** Frozen — 规则变更需通过 spec 流程

---

## 单一规则源原则

**所有 EWU / RWU / SWU 的计算规则只在一个位置定义:**

```
apps/core-api/app/domain/ewu.py      — EWU 唯一权威
apps/core-api/app/domain/rwu_swu.py  — RWU / SWU 唯一权威
apps/core-api/app/domain/quota_config.py — 上限规则唯一权威
```

**任何消费者（MCP Server、前端、Temporal、测试）不得维护独立公式副本。**

升级规则时，只修改上述文件。

---

## EWU (Effort Work Unit) — 基础工作量单位

### 定义

EWU 表达任务的工作量大小，用于匹配、分层、经验沉淀。EWU 不直接等于积分价值。

### 计算公式

```
EWU = base_weight(task_type) × avg(complexity, criticality, collaboration_complexity) × risk_multiplier
```

### 输入参数

| 参数 | 类型 | 范围 |
|------|------|------|
| task_type | Literal | requirement_clarification, research, product_design, development, testing_fix, documentation, collaboration_support, review_audit |
| risk_level | Literal | low, medium, high |
| complexity | int | 1-5 |
| criticality | int | 1-5 |
| collaboration_complexity | int | 1-5 |

### 权重表

| task_type | base_weight |
|-----------|-------------|
| requirement_clarification | 0.8 |
| research | 1.0 |
| product_design | 1.2 |
| development | 1.5 |
| testing_fix | 1.0 |
| documentation | 0.7 |
| collaboration_support | 0.6 |
| review_audit | 0.9 |

### 风险乘数

| risk_level | multiplier |
|------------|-----------|
| low | 1.0 |
| medium | 1.3 |
| high | 1.6 |

### 上限

- 单任务 EWU 不得超过 **8**
- 在 preflight 和 CRUD (create/update/calculate) 双层阻断

---

## RWU (Reward Work Unit) — 招募激励单位

### 定义

RWU 是招募项目 (`has_reward=True`) 的激励工作量单位，基于 EWU 换算。

### v1 公式 (frozen)

```
RWU = EWU × 1.2
```

v1 使用固定 standard tier 乘数。tier 参数预留但暂不对外开放。

### 触发条件

仅当 `project.has_reward == True` 且 EWU 存在时计算。

---

## SWU (Sponsor Work Unit) — 公益激励单位

### 定义

SWU 是公益 sponsor 项目 (`has_sponsor=True`) 的补充激励单位，基于 EWU 换算。

### v1 公式 (frozen)

```
SWU = EWU × 1.0
```

v1 中 SWU 与 EWU 等值。设计意图：公益项目的补充激励在 v1 先与基础工作量保持一致，后续由产品定义差异化系数。

### 触发条件

仅当 `project.has_sponsor == True` 且 EWU 存在时计算。

---

## 聚合规则

### Work Package 层 (v1)

| 字段 | 公式 |
|------|------|
| total_ewu | SUM(task_cards.ewu) for WP's tasks |
| avg_ewu | AVG(task_cards.ewu) for WP's tasks |
| total_rwu | SUM(task_cards.rwu) for WP's tasks (nullable) |
| total_swu | SUM(task_cards.swu) for WP's tasks (nullable) |
| task_count | COUNT(task_cards) for WP's tasks |

### Project 层 (v1)

| 字段 | 公式 |
|------|------|
| total_ewu | SUM(task_cards.ewu) for project's tasks |
| avg_ewu | AVG(task_cards.ewu) for project's tasks |
| max_ewu | MAX(task_cards.ewu) for project's tasks |
| total_rwu | SUM(task_cards.rwu) for project's tasks (nullable) |
| total_swu | SUM(task_cards.swu) for project's tasks (nullable) |
| task_count | COUNT(task_cards) for project's tasks |

### 实现方式

Response Aggregation — 在 service 层按需计算，不在主表存冗余列。

### project_complexity_score

`project_complexity_score` 是**分析指标**，不是正式工作量单位，不替代 `total_ewu`。

---

## 联动规则

| 事件 | RWU 行为 | SWU 行为 |
|------|----------|----------|
| task create (has_reward) | 自动计算 | — |
| task create (has_sponsor) | — | 自动计算 |
| task update (ewu 变化 + has_reward) | 自动重算 | — |
| task update (ewu 变化 + has_sponsor) | — | 自动重算 |
| calculate-ewu (has_reward) | 自动重算 | — |
| calculate-ewu (has_sponsor) | — | 自动重算 |

---

## 默认值

| 字段 | Schema default | Model default |
|------|---------------|---------------|
| ewu | Decimal("1.0") | Decimal("1.00") |
| rwu | None | None |
| swu | None | None |
