copy into ${name} ( S3_OBJECT_NAME, PAYLOAD )
from (select METADATA$FILENAME, $1 from @${name} )
file_format = ( type = parquet )
