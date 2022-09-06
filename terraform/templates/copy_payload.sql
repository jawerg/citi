copy into ${name} ( PAYLOAD )
from (select $1 from @${name} )
file_format = ( type = parquet )
