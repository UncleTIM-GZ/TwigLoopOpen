-- Twig Loop ClickHouse 初始化
-- 基础事件表，用于接收 NATS 事件流的分析数据

CREATE TABLE IF NOT EXISTS twigloop_analytics.events (
    event_id UUID DEFAULT generateUUIDv4(),
    event_type String,
    event_version UInt8 DEFAULT 1,
    source_service String,
    actor_id Nullable(UUID),
    resource_type Nullable(String),
    resource_id Nullable(UUID),
    payload String DEFAULT '{}',
    created_at DateTime64(3) DEFAULT now64(3),
    trace_id String DEFAULT ''
) ENGINE = MergeTree()
ORDER BY (event_type, created_at)
PARTITION BY toYYYYMM(created_at)
TTL toDateTime(created_at) + INTERVAL 365 DAY;

-- 页面浏览表
CREATE TABLE IF NOT EXISTS twigloop_analytics.page_views (
    view_id UUID DEFAULT generateUUIDv4(),
    actor_id Nullable(UUID),
    session_id String,
    page_path String,
    referrer String DEFAULT '',
    user_agent String DEFAULT '',
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
ORDER BY (page_path, created_at)
PARTITION BY toYYYYMM(created_at)
TTL toDateTime(created_at) + INTERVAL 180 DAY;

-- Signal aggregation MV: count signals per project per day
CREATE MATERIALIZED VIEW IF NOT EXISTS twigloop_analytics.mv_project_signals_daily
ENGINE = SummingMergeTree()
ORDER BY (project_id, signal_date)
AS SELECT
    resource_id AS project_id,
    toDate(created_at) AS signal_date,
    count() AS signal_count
FROM twigloop_analytics.events
WHERE event_type LIKE 'source.signal%'
GROUP BY project_id, signal_date;
