select
    -- binary variable for subscriber/customer with sub = 1.
    decode(
            usertype,
            'Subscriber', 1,
            'Customer', 0,
            null
        )                        as "is subscriber",

    -- kept variables from the source dataset
    gender,
    tripduration,

    -- extract parts from start timestamp for categorical variables.
    dayofweek(starttime)         as "start dow",
    hour(starttime)              as "start hour",

    -- computed entities
    year(starttime) - birth_year as "customer age",
    (
            1000 * haversine(
                start_station_latitude,
                start_station_longitude,
                end_station_latitude,
                end_station_longitude
            )
        )::number(10, 0)         as "trip distance in m",
    (
            (trip_distance_in_m::float / 1000.0)
            / (tripduration::float / 60.0)
        )::number(10, 0)         as "trip speed km/h"
from {{ ref('tripdata') }}
where is_subscriber is not null