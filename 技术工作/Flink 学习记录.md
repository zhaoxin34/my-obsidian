# SQL 使用方法

##  查询

### [窗口查询示例](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/table/sql/queries/window-agg/)

* `TUMBLE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '10' MINUTES)`
    * 每10分钟划分一个窗口 
* `HOP(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES)`
	* 起始时间(start_time)按照每5分钟划分一个窗口，窗口大小是10分钟
* `CUMULATE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES)`
	* 起始时间(start_time)每10分钟一个窗口，窗口大小以2累加，就是2、4、6、8、10
* `SESSION(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '2' MINUTES)`
	* 2分钟一个session窗口
* `SESSION(TABLE Bid PARTITION BY supplier_id, DESCRIPTOR(bidtime), INTERVAL '2' MINUTES)`
	* 2分钟一个session窗口，并且按照spplier_id做分区

假设有如下要给做空记录表, 包含了做空时间、金额等字段
```sql
Flink SQL> SELECT * FROM Bid;
+------------------+-------+------+-------------+
|          bidtime | price | item | supplier_id |
+------------------+-------+------+-------------+
| 2020-04-15 08:05 | 4.00  | C    | supplier1   |
| 2020-04-15 08:07 | 2.00  | A    | supplier1   |
| 2020-04-15 08:09 | 5.00  | D    | supplier2   |
| 2020-04-15 08:11 | 3.00  | B    | supplier2   |
| 2020-04-15 08:13 | 1.00  | E    | supplier1   |
| 2020-04-15 08:17 | 6.00  | F    | supplier2   |
+------------------+-------+------+-------------+
```

```sql
-- tumbling window aggregation
Flink SQL> SELECT window_start, window_end, SUM(price) AS total_price
  FROM TUMBLE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '10' MINUTES)
  GROUP BY window_start, window_end;
+------------------+------------------+-------------+
|     window_start |       window_end | total_price |
+------------------+------------------+-------------+
| 2020-04-15 08:00 | 2020-04-15 08:10 |       11.00 |
| 2020-04-15 08:10 | 2020-04-15 08:20 |       10.00 |
+------------------+------------------+-------------+
```

```sql
-- hopping window aggregation
Flink SQL> SELECT window_start, window_end, SUM(price) AS total_price
  FROM HOP(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES)
  GROUP BY window_start, window_end;
+------------------+------------------+-------------+
|     window_start |       window_end | total_price |
+------------------+------------------+-------------+
| 2020-04-15 08:00 | 2020-04-15 08:10 |       11.00 |
| 2020-04-15 08:05 | 2020-04-15 08:15 |       15.00 |
| 2020-04-15 08:10 | 2020-04-15 08:20 |       10.00 |
| 2020-04-15 08:15 | 2020-04-15 08:25 |        6.00 |
+------------------+------------------+-------------+
```

```sql
-- cumulative window aggregation
Flink SQL> SELECT window_start, window_end, SUM(price) AS total_price
  FROM CUMULATE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES)
  GROUP BY window_start, window_end;
+------------------+------------------+-------------+
|     window_start |       window_end | total_price |
+------------------+------------------+-------------+
| 2020-04-15 08:00 | 2020-04-15 08:06 |        4.00 |
| 2020-04-15 08:00 | 2020-04-15 08:08 |        6.00 |
| 2020-04-15 08:00 | 2020-04-15 08:10 |       11.00 |
| 2020-04-15 08:10 | 2020-04-15 08:12 |        3.00 |
| 2020-04-15 08:10 | 2020-04-15 08:14 |        4.00 |
| 2020-04-15 08:10 | 2020-04-15 08:16 |        4.00 |
| 2020-04-15 08:10 | 2020-04-15 08:18 |       10.00 |
| 2020-04-15 08:10 | 2020-04-15 08:20 |       10.00 |
+------------------+------------------+-------------+
```

```sql
-- session window aggregation with partition keys
Flink SQL> SELECT window_start, window_end, supplier_id, SUM(price) AS total_price
           FROM SESSION(TABLE Bid PARTITION BY supplier_id, DESCRIPTOR(bidtime), INTERVAL '2' MINUTES)
           GROUP BY window_start, window_end, supplier_id;
+------------------+------------------+-------------+-------------+
|     window_start |       window_end | supplier_id | total_price |
+------------------+------------------+-------------+-------------+
| 2020-04-15 08:05 | 2020-04-15 08:09 | supplier1   |        6.00 |
| 2020-04-15 08:09 | 2020-04-15 08:13 | supplier2   |        8.00 |
| 2020-04-15 08:13 | 2020-04-15 08:15 | supplier1   |        1.00 |
| 2020-04-15 08:17 | 2020-04-15 08:19 | supplier2   |        6.00 |
+------------------+------------------+-------------+-------------+

-- session window aggregation without partition keys
Flink SQL> SELECT window_start, window_end, SUM(price) AS total_price
           FROM SESSION(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '2' MINUTES)
           GROUP BY window_start, window_end;
+------------------+------------------+-------------+
|     window_start |       window_end | total_price |
+------------------+------------------+-------------+
| 2020-04-15 08:05 | 2020-04-15 08:15 |       15.00 |
| 2020-04-15 08:17 | 2020-04-15 08:19 |        6.00 |
+------------------+------------------+-------------+
```