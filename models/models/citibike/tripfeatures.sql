select
    -- binary variable for subscriber/customer with sub = 1.
    decode(
            usertype,
            'Subscriber', 1,
            'Customer', 0,
            null
        )                        as is_subscriber,

    -- kept variables from the source dataset
    gender,
    tripduration,

    -- extract parts from start timestamp for categorical variables.
    dayofweek(starttime)         as start_dow,
    hour(starttime)              as start_hour,

    -- computed entities
    year(starttime) - birth_year as customer_age,
    (
            1000 * haversine(
                start_station_latitude,
                start_station_longitude,
                end_station_latitude,
                end_station_longitude
            )
        )::number(10, 0)         as trip_distance_in_m,
    (
            trip_distance_in_m::float
            / tripduration::float
        )::number(10, 0)         as trip_speed_m_per_min
from {{ ref('tripdata') }}
where is_subscriber is not null