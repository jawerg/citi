select
    s3_object_name,
    payload:"bikeid"::number(20,0)              as bikeid,
    payload:"birth year"::number(4,0)           as birth_year,
    payload:"end station id"::number(10,0)      as end_station_id,
    payload:"end station latitude"::float       as end_station_latitude,
    payload:"end station longitude"::float      as end_station_longitude,
    payload:"end station name"::varchar(1024)   as end_station_name,
    payload:"gender"::number(1,0)               as gender,
    payload:"start station id"::number(10,0)    as start_station_id,
    payload:"start station latitude"::float     as start_station_latitude,
    payload:"start station longitude"::float    as start_station_longitude,
    payload:"start station name"::varchar(1024) as start_station_name,
    payload:"starttime"::timestamp_ntz(4)       as starttime,
    payload:"stoptime"::timestamp_ntz(4)        as stoptime,
    payload:"tripduration"::number(10,0)        as tripduration,
    payload:"usertype"::varchar(16)             as usertype
from {{ source('citibike', 'tripdata') }}
