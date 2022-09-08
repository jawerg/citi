select
    payload:"datetime"::date as datetime,
    payload:"conditions"::varchar(32) as conditions,
    payload:"feelslike"::float as feelslike,
    payload:"feelslikemax"::float as feelslikemax,
    payload:"feelslikemin"::float as feelslikemin,
    payload:"humidity"::float as humidity,
    payload:"moonphase"::float as moonphase,
    payload:"sealevelpressure"::float as sealevelpressure,
    payload:"snow"::float as snow,
    payload:"snowdepth"::float as snowdepth,
    payload:"solarradiation"::float as solarradiation,
    payload:"uvindex"::number(2) as uvindex,
    payload:"winddir"::float as winddir,
    payload:"windgust"::float as windgust,
    payload:"windspeed"::float as windspeed
from {{ source('citibike', 'wetterdaten') }}