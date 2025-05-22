CREATE DATABASE IF NOT EXISTS data_analytics;


CREATE TABLE IF NOT EXISTS data_analytics.event_table_shard1 (
    id UUID,
    user_id UUID,
    movie_id UUID,
    action String,
    event_data String,
    event_time DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard1/event_table', '{replica}')
  PARTITION BY toYYYYMMDD(event_time)
  ORDER BY (event_time, id);


CREATE TABLE IF NOT EXISTS data_analytics.event_table_shard2 (
    id UUID,
    user_id UUID,
    movie_id UUID,
    action String,
    event_data String,
    event_time DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/shard2/event_table', '{replica}')
  PARTITION BY toYYYYMMDD(event_time)
  ORDER BY (event_time, id);


CREATE TABLE IF NOT EXISTS default.event_table (
    id UUID,
    user_id UUID,
    movie_id UUID,
    action String,
    event_data String,
    event_time DateTime
) ENGINE = Distributed('company_cluster', 'data_analytics', 'event_table_shard{h}', cityHash64(user_id));
