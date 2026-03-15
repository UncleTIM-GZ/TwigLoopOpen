# Twig Loop Public Repo 发布执行计划

## 安全审计结论

**风险等级: LOW** — 无已提交的真实凭证或安全泄漏。

已验证:
- `.env` 未提交 (在 `.gitignore` 中)
- 无硬编码 API 密钥
- 无真实邮箱/用户数据
- 测试用虚拟数据和 SQLite in-memory
- docker-compose 使用本地开发默认凭证

## 公开范围

### 建议公开

| 目录 | 说明 | 安全状态 |
|------|------|----------|
| apps/core-api/ | 后端 API (FastAPI) | SAFE |
| apps/web/ | 前端 (Next.js) | SAFE |
| apps/mcp-server/ | MCP Server | SAFE |
| packages/ | 共享包 (schemas, auth, events, config, observability) | SAFE |
| workflows/ | Temporal workflows | SAFE |
| skills/ | MCP Skills 定义 | SAFE |
| docker-compose.yml | 基础设施 (加 dev-only 标注) | SAFE |
| .env.example | 环境变量模板 | SAFE |
| scripts/ | 数据库初始化 SQL | SAFE |
| tests/ | 全量测试 | SAFE |
| .github/ | CI workflow | SAFE |
| docs/ | 文档 (pilot, beta, plans, rules) | SAFE |
| .docs/ | 设计文档 (PRD, 架构, ERD) | SAFE |
| .claude/ | 开发规则 | SAFE |
| .dev/ | 进度追踪 | SAFE |

### 建议不公开 / 需处理

| 项目 | 处理方式 |
|------|----------|
| `.env` 物理文件 | 不在 git 中，确认不提交 |
| docker-compose.yml 凭证注释 | 添加 "LOCAL DEV ONLY" 标注 |
| 根目录 `TwigLoop PRD V1.md` | 未追踪文件，清理 |
| apps/source-sync-worker/ | 代码可公开但标注为 WIP |
| apps/mcp-orchestrator/ | 已废弃，可公开但标注 DEPRECATED |

## 导出方案

**建议: 直接将当前仓库改为 public**，原因:
1. Git 历史无敏感信息泄漏
2. 所有代码和文档已通过安全审计
3. 无需 squash 或重建历史
4. `.gitignore` 已正确配置

**替代方案 (如需独立 public repo):**
```bash
# 从私有仓导出到新 public repo
git clone --bare <private-repo-url> twigloop-public.git
cd twigloop-public.git
# 移除任何不需要的分支
git branch -D <internal-branches>
# 推送到新的 public repo
git push --mirror <new-public-repo-url>
```

## 执行阶段

### Phase 1: 文档与开源文件 (本轮)
- [x] 安全审计
- [ ] README.md (public 版)
- [ ] LICENSE
- [ ] CONTRIBUTING.md
- [ ] SECURITY.md
- [ ] CODE_OF_CONDUCT.md
- [ ] .github/ISSUE_TEMPLATE/
- [ ] .github/PULL_REQUEST_TEMPLATE.md
- [ ] docker-compose 加标注

### Phase 2: 清理与验证
- [ ] 删除根目录多余文件
- [ ] 本地完整运行验证
- [ ] 文档链接检查
- [ ] 最终安全扫描

### Phase 3: 发布
- [ ] 设置仓库为 Public
- [ ] 发布 Release (v0.9.3-public-beta)
- [ ] 通知 Beta 用户
