CREATE DATABASE shard;

CREATE TABLE shard.event_table (
    id UUID,
    user_id UUID,
    movie_id UUID,
    action String,
    event_data String,
    event_time DateTime
) Engine=ReplicatedMergeTree('/clickhouse/tables/{shard}/event_table', '{replica}')
PARTITION BY toYYYYMMDD(event_time)
ORDER BY id;

CREATE TABLE default.event_table (
    id UUID,
    user_id UUID,
    movie_id UUID,
    action String,
    event_data String,
    event_time DateTime
) ENGINE = Distributed('{cluster}', '', event_table, rand());
