{{
  config(
    materialized='table',
    cluster_by=['is_subscriber', 'gender']
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
    tripduration                 as tripduration,

    -- extract parts from start timestamp for categorical variables.
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
    (
        (1.0 * trip_distance_in_km)
        / (tripduration::float / 60.0 / 60.0)
    )         as trip_speed_kmh
from {{ ref('tripdata') }}
where is_subscriber is not null

-- Sort outputs by broad categories to improve compression of output file
order by
    is_subscriber,
    gender,
    customer_age