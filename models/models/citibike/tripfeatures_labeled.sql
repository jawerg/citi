select
    decode(is_subscriber, 1, 'Subscriber', 0, 'Customer', null) as is_subscriber,
    decode(gender, 0, 'Unknown', 1, 'Male', 2, 'Female', null) as gender,
    tripduration,
    decode(
            start_dow,
            0, 'So',
            1, 'Mo',
            2, 'Di',
            3, 'Mi',
            4, 'Do',
            5, 'Fr',
            6, 'Sa'
        ) as start_dow,
    start_hour,
    customer_age,
    trip_distance_in_km,
    trip_speed_kmh
from {{ ref('tripfeatures') }}