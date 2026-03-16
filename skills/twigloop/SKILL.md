---
name: twigloop
description: Twig Loop 项目协作平台 — 通过 MCP Server 发布项目、管理工作包和任务卡、申请协作
---

# Twig Loop Skills

你正在与 Twig Loop 协作平台交互。平台帮助发起者将想法转化为结构化项目，并匹配合适的协作者。

## 可用 MCP Tools

以下工具通过标准 MCP Server 提供：

### 认证
- `register_actor` — 注册新用户
- `authenticate_actor` — 登录获取 access token
- `get_actor_profile` — 查看当前用户资料

### 项目管理
- `list_projects` — 浏览开放项目
- `get_project` — 查看项目详情
- `create_project` — 创建项目
- `apply_to_project` — 申请加入项目
- `review_applicants` — 查看申请者（发起者）

### 编排（一键发布）
- `publish_project_bundle` — 一键创建项目 + 工作包 + 任务卡
- `draft_work_package` — 创建工作包草稿
- `validate_task_card` — 校验任务卡质量
- `calculate_ewu` — 计算任务工作量 (EWU)

### 上下文查询
- `get_publish_rules` — 获取指定项目类型的发布规则（必填字段、人工复核等）
- `get_project_schema` — 获取项目、工作包、任务卡的完整字段定义
- `get_actor_context` — 获取当前用户资料 + 活跃项目列表

### 草稿管理
- `create_draft` — 创建草稿（渐进式收集项目/申请数据）
- `update_draft` — 更新草稿字段
- `get_draft` — 查看草稿详情
- `list_my_drafts` — 列出我的所有草稿
- `delete_draft` — 删除草稿

### 预检验证
- `preflight_project` — 对项目草稿运行预检（字段完整性、规则合规）
- `preflight_application` — 检查当前用户是否有资格申请某项目

## 技能（Skills）

技能是多步操作的编排模板，位于 `skills/twigloop/skills/` 目录：

| 技能 | 用途 |
|------|------|
| `publish_project` | 引导用户发布完整项目：收集 → 预检 → 发布 |
| `apply_to_task` | 引导用户申请协作：资格检查 → 提交申请 |
| `preflight_project` | 对草稿运行预检验证 |
| `explain_rules` | 向用户解释平台规则 |

## 项目发布向导

如果用户想发布一个新项目，请按以下步骤引导：

1. **确认项目类型**：调用 `get_publish_rules` 了解规则
2. **创建草稿**：调用 `create_draft` 开始收集信息
3. **渐进收集**：多轮对话中用 `update_draft` 逐步补充字段
4. **获取模式**：需要时调用 `get_project_schema` 了解字段要求
5. **结构化工作包**：将项目拆分为工作包和任务卡
6. **校验任务卡**：用 `validate_task_card` 检查每个任务
7. **计算 EWU**：用 `calculate_ewu` 评估工作量
8. **预检**：用 `preflight_project` 验证完整性
9. **一键发布**：用 `publish_project_bundle` 完成发布

## 项目类型说明

| 类型 | 说明 | 发起者 |
|------|------|--------|
| general | 一般开发项目 | 个人或组织 |
| public_benefit | 公益项目（需人工复核） | 弱势群体/公益机构 |
| recruitment | 招募项目（有预算激励） | 贡献者 |

## 注意事项

- 所有写入操作需要 `access_token`，先调用 `authenticate_actor` 获取
- 公益项目在关键节点需要人工复核，不可跳过
- MCP Server 不直接写数据库，所有数据通过 core-api 写入
- 草稿是临时状态，仅用于 AI 辅助收集，最终发布仍通过 `publish_project_bundle`
