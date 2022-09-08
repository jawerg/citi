resource "snowflake_table" "citibike_wetterdaten" {
  database            = snowflake_database.cb.name
  schema              = snowflake_schema.lz.name
  name                = "WETTERDATEN"
  comment             = ""
  data_retention_days = 1
  change_tracking     = false

  column {
    name = "S3_OBJECT_NAME"
    type = "VARCHAR(1024)"
    nullable = false
  }

  column {
    name     = "PAYLOAD"
    type     = "VARIANT"
    nullable = false
  }
}


resource "snowflake_stage" "citibike_wetterdaten" {
  name = snowflake_table.citibike_wetterdaten.name
  url = "s3://snowflake-f28c31-3e92-9edc-c7f2-aab9-9a0c-889436/wergstatt/citibike/wetterdaten/"
  database            = snowflake_database.cb.name
  schema              = snowflake_schema.lz.name
  storage_integration = "SCHNEEFLOCKE"
}

resource "snowflake_pipe" "citibike_wetterdaten" {
  database = snowflake_database.cb.name
  schema   = snowflake_schema.lz.name
  name     = snowflake_table.citibike_wetterdaten.name

  auto_ingest = true
  copy_statement = templatefile(
    "${path.module}/templates/copy_payload.sql",
    { "name" = replace(snowflake_table.citibike_wetterdaten.id, "|", ".") }
  )

  depends_on = [
    snowflake_table.citibike_wetterdaten,
    snowflake_stage.citibike_wetterdaten
  ]
}