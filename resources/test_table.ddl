use temporary;

create table if not exists `mock_1`(
    `vin` char(17) primary key ,
    `car_model` varchar(40),
    `car_make` varchar(40),
    `car_model_year` char(4),
    `color` varchar(20),
    `created_at` datetime,
    `num` decimal(6,3)
);

create table if not exists `mock_2`(
    `vin` char(17) primary key ,
    `car_model` varchar(40),
    `car_mk` varchar(40),
    `car_model_yyyy` char(4),
    `color` varchar(20),
    `created_at` datetime,
    `num` decimal(6,3)
);


LOAD DATA INFILE 'MOCK_DATA_1.csv' INTO TABLE `mock_1`
    CHARACTER SET utf8
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (@vin, @car_model, @car_make, @car_model_year, @color, @created_at, @num)
SET
     `vin` = @vin
    ,`car_model` = @car_model
    ,`car_make` = @car_make
    ,`car_model_year` = @car_model_year
    ,`color` = @color
    ,`created_at` = @created_at
    ,`num` = @num
;

LOAD DATA INFILE 'MOCK_DATA_2.csv' INTO TABLE `mock_2`
    CHARACTER SET utf8
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (@vin, @car_model, @car_mk, @car_model_yyyy, @color, @created_at, @num)
SET
     `vin` = @vin
    ,`car_model` = @car_model
    ,`car_mk` = @car_mk
    ,`car_model_yyyy` = @car_model_yyyy
    ,`color` = @color
    ,`created_at` = @created_at
    ,`num` = @num
;

create table if not exists `mock_3`(
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