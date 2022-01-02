#!/bin/sh/env bash

### hdfs에 csv파일 put
hdfs dfs -put MOCK_DATA_1.csv /user/test/MOCK_DATA_1.csv
hdfs dfs -put MOCK_DATA_2.csv /user/test/MOCK_DATA_2.csv


### Table 생성
hive -e "
create external table if not exists `mock_1`(
    `vin` char(17) primary key,
    `car_model` varchar(40),
    `car_make` varchar(40),
    `car_model_year` char(4),
    `color` varchar(20),
    `created_at` datetime,
    `num` decimal(6,3)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION
  'hdfs://nameservice1/user/hive/warehouse/temporary.db/mock_1'
"

### Table 생성
hive -e "
create external table if not exists `mock_2`(
    `vin` char(17) primary key ,
    `car_model` varchar(40),
    `car_mk` varchar(40),
    `car_model_yyyy` char(4),
    `color` varchar(20),
    `created_at` datetime,
    `num` decimal(6,3)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION
  'hdfs://nameservice1/user/hive/warehouse/temporary.db/mock_2'
"

### load csv data on HDFS
hive -e "LOAD DATA INPATH '/user/test/MOCK_DATA_1.csv' OVERWRITE INTO TABLE temporary.mock_1"
hive -e "LOAD DATA INPATH '/user/test/MOCK_DATA_2.csv' OVERWRITE INTO TABLE temporary.mock_2"


### Table 생성
hive -e "
create external table if not exists `mock_3`(
    `vin` char(17) primary key ,
    `car_model` varchar(40),
    `car_mk` varchar(40),
    `car_model_yyyy` char(4),
    `color` varchar(20),
    `created_at` datetime,
    `numb` decimal(6,3)
) as
    select `vin`
         , `car_model`
         , `car_make` as `car_mk`
         , `car_model_year` as `car_model_yyyy`
         , concat(`color`, `color`) as `color`
         , `created_at`
         , `num` + 1 as `numb`
      from `mock_1`
"
