{{
  config(
    materialized='table',
    cluster_by=['is_subscriber', 'start_month', 'gender']
  )
}}

select
    -- binary variable for subscriber/customer with sub = 1.
    decode(
            usertype,
            'Subscriber', 1,
            'Customer', 0,
            null
        )                        as is_subscriber,

    -- kept variables from the source dataset
    gender                       as gender,
    tripduration  / 3600.0       as tripduration_in_h,

    -- extract parts from start timestamp for categorical variables.
    starttime::date              as trip_date,
    year(starttime)              as start_year,
    month(starttime)             as start_month,
    dayofweek(starttime)         as start_dow,
    hour(starttime)              as start_hour,

    -- computed entities
    year(starttime) - birth_year as customer_age,
    haversine(
        start_station_latitude,
        start_station_longitude,
        end_station_latitude,
        end_station_longitude
    )         as trip_distance_in_km,
    trip_distance_in_km / tripduration_in_h as trip_speed_kmh
from {{ ref('tripdata') }}
where is_subscriber is not null

-- Sort outputs by broad categories to improve compression of output file
order by
    is_subscriber,
    start_month,
    gender