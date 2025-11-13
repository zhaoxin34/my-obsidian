## 导出到minio或者hdfs的sql

```sql
INSERT INTO 
FILES(
    "path" = "s3://temp/data3",
    "format" = "parquet",
    "single" = "true",
    "aws.s3.access_key" = "admin",
    "aws.s3.secret_key" = "Datatist1506",
    "aws.s3.region" = "datatist",
    "aws.s3.use_instance_profile" = "false",
    "aws.s3.enable_ssl" = "false",
    "aws.s3.enable_path_style_access" = "true",
    "aws.s3.endpoint" = "http://minio-svc.store.svc.cluster.local:19000"
)
SELECT * FROM dt_benefit_info;
```

```sql
INSERT INTO 
FILES(
    "path" = "hdfs://hadoop-master-svc.bigdata-test.svc.cluster.local:8020/tmp/test_2233",
    "format" = "parquet",
    "compression" = "snappy"
)
SELECT * FROM dt_user_info;
```

## 从minio导入到表

```sql
insert into tmp_dt_user_info(scenario_code, dt_id, name, gender, age, city, create_time, balance)
select * from
FILES(
    "path" = "s3://temp/dt_user_info/*.csv",
    "format" = "csv",
    "csv.column_separator"=",",
    "single" = "true",
    "aws.s3.access_key" = "admin",
    "aws.s3.secret_key" = "Datatist1506",
    "aws.s3.region" = "datatist",
    "aws.s3.use_instance_profile" = "false",
    "aws.s3.enable_ssl" = "false",
    "aws.s3.enable_path_style_access" = "true",
    "aws.s3.endpoint" = "http://minio-svc.store.svc.cluster.local:19000"
)
limit 10;
```