select
    decode(is_subscriber, 1, 'Subscriber', 0, 'Customer', null) as is_subscriber,
    decode(gender, 0, 'Unknown', 1, 'Male', 2, 'Female', null) as gender,
    tripduration_in_h,
    decode(
            start_dow,
            0, '0 Sunday',
            1, '1 Monday',
            2, '2 Tuesday',
            3, '3 Wednesday',
            4, '4 Thursday',
            5, '5 Friday',
            6, '6 Saturday'
        ) as start_dow,
    decode(
            start_month,
            1, '01 January',
            2, '02 February',
            3, '03 March',
            4, '04 April',
            5, '05 May',
            6, '06 June',
            7, '07 July',
            8, '08 August',
            9, '09 September',
            10, '10 October',
            11, '11 November',
            12, '12 December'
        ) as start_month,
    start_hour,
    customer_age,
    trip_distance_in_km,
    trip_speed_kmh
from {{ ref('tripfeatures') }}