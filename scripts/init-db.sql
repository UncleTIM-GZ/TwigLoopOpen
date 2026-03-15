-- Twig Loop PostgreSQL 初始化
-- 该脚本由 docker-entrypoint-initdb.d 自动执行（仅首次启动）

-- 主业务数据库已由 POSTGRES_DB 环境变量创建
-- 这里创建 Temporal 需要的额外数据库

CREATE DATABASE temporal;
CREATE DATABASE temporal_visibility;

-- 授权
GRANT ALL PRIVILEGES ON DATABASE temporal TO twigloop;
GRANT ALL PRIVILEGES ON DATABASE temporal_visibility TO twigloop;

-- 启用 uuid-ossp 扩展（主库）
\c twigloop;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
