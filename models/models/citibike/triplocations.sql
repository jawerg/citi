with 
locations as (
    select 
        start_station_id        as station_id,
        start_station_name      as station_name,
        start_station_latitude  as station_lat,
        start_station_longitude as station_lon
    from {{ ref('tripdata') }}
    
    union all 
    
    select 
        end_station_id,
        end_station_name,
        start_station_latitude,
        start_station_longitude
    from {{ ref('tripdata') }}
),

normalized_locations as (
    select 
        station_id       as id,
        station_name     as name,
        avg(station_lat) as lat,
        avg(station_lon) as lon
    from locations
    where station_id is not null
    group by 1,2
    order by 1
)

select
    usertype            as is_subscriber,
    gender,
    
    start_station_id,
    start_station_name,
    start_location.lat  as start_station_lat,
    start_location.lon  as start_station_lon,
    
    end_station_id,
    end_station_name,
    end_location.lat    as end_station_lat,
    end_location.lon    as end_station_lon
    
from {{ ref('tripdata') }}              as tripdata
    inner join normalized_locations     as start_location
        on tripdata.start_station_id = start_location.id
    inner join normalized_locations     as end_location
        on tripdata.end_station_id = end_location.id