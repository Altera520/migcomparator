# migcomparator

[![PyPI version](https://badge.fury.io/py/migcomparator.svg)](https://badge.fury.io/py/migcomparator)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

> Apache Hive와 MariaDB(or MySQL)에 위치한 테이블의 데이터를 Pandas를 통해 비교해주는 라이브러리입니다. 

- [Install](#install)
- [Basic Usage](#basic-usage)
  - [테이블간의 데이터 건수 비교](#테이블간의-데이터-건수-비교)
  - [테이블간의 대칭차집합](#테이블간의-대칭차집합)
  - [테이블간의 불일치 데이터 추출](#테이블간의-불일치-데이터-추출)
- [User Component](#User-Component)
  - [Table](#table)
  - [ColumnPair](#columnpair)
  - [Connector](#connector)
  - [Validator](#validator)

## Install

```bash
pip install migcomparator
```

## Basic usage

#### MariaDB Mock data 

```plain
> select * from `mock_1` limit 3
+-----------------+-------------+--------+--------------+---------+-------------------+------+
|vin              |car_model    |car_make|car_model_year|color    |created_at         |num   |
+-----------------+-------------+--------+--------------+---------+-------------------+------+
|19UUA56763A081084|Rodeo        |Isuzu   |2000          |Goldenrod|2021-11-18 08:38:22|57.064|
|19UUA65545A837147|Amanti       |Kia     |2004          |Yellow   |2021-07-07 13:32:59|NULL  |
|19UUA65566A654351|B-Series Plus|Mazda   |2000          |Orange   |2021-07-25 05:39:41|NULL  |
+-----------------+-------------+--------+--------------+---------+-------------------+------+
```

#### Apache Hive Mock data

```plain
> select * from `mock_2` limit 3
+-----------------+---------+----------+--------------+---------+-------------------+------+
|vin              |car_model|car_mk    |car_model_yyyy|color    |created_at         |num   |
+-----------------+---------+----------+--------------+---------+-------------------+------+
|19UUA65684A456148|Discovery|Land Rover|1996          |Violet   |2021-04-18 11:25:59|42.526|
|19UUA66228A764918|GTO      |Mitsubishi|1994          |Yellow   |2021-10-25 23:41:01|10.004|
|19UUA66267A272004|Corvette |Chevrolet |1960          |Puce     |2021-02-26 19:25:45|NULL  |
+-----------------+---------+----------+--------------+---------+-------------------+------+

> select * from `mock_3` limit 3
+-----------------+-------------+------+--------------+------------------+-------------------+------+
|vin              |car_model    |car_mk|car_model_yyyy|color             |created_at         |numb  |
+-----------------+-------------+------+--------------+------------------+-------------------+------+
|19UUA56763A081084|Rodeo        |Isuzu |2000          |GoldenrodGoldenrod|2021-11-18 08:38:22|58.064|
|19UUA65545A837147|Amanti       |Kia   |2004          |YellowYellow      |2021-07-07 13:32:59|NULL  |
|19UUA65566A654351|B-Series Plus|Mazda |2000          |OrangeOrange      |2021-07-25 05:39:41|NULL  |
+-----------------+-------------+------+--------------+------------------+-------------------+------+

```

### 테이블간의 데이터 건수 비교

#### MariaDB(or MySQL) to Apache Hive
```python
from migcomparator.models.pandas_validator import PandasValidator
from migcomparator.models.table import Table
from migcomparator.query_sender.connector import MariadbConnector, HiveConnector

# create datasource connector
mariadb_sender = \ 
        MariadbConnector(
            host='localhost',
            port=3306,
            user='username',
            password='password',
            database='schema'
        )

hive_sender = \ 
        HiveConnector(
            host='localhost',
            port=10000,
            user='username',
            password='password',
            database='schema',
            auth_mechanism='PLAIN'
        )

# create source & target logical table
source = Table(name='mock_1', sender=mariadb_sender) \
            .where("date_format(`created_at`, '%Y%m%d') = '20220101'") \
            .where("`vin` = 'fakevin'")

# Hive 테이블은 pk를 명시적으로 지정
target = Table(name='mock_2', sender=hive_sender, pk=['vin']) \
            .where("date_format(created_at, 'yyyyMMdd') = '20220101'") \
            .where("`vin` = 'fakevin'")

# count compare, PairResult 객체 반환
pair_result = PandasValidator.count_compare(
    source=source, target=target
)
```

#### PairResult 결과

```plain
(source: 1000, target: 850, match: False)
```

### 테이블간의 대칭차집합

#### MariaDB(or MySQL) to Apache Hive
```python
from migcomparator.models.pandas_validator import PandasValidator
from migcomparator.models.table import Table
from migcomparator.query_sender.connector import MariadbConnector, HiveConnector

...

# create source & target logical table
source = Table(name='mock_1', sender=mariadb_sender) \
            .where("date_format(`created_at`, '%Y%m%d') = '20220101'") \
            .where("`vin` = 'fakevin'")

# Hive 테이블은 pk를 명시적으로 지정
target = Table(name='mock_2', sender=hive_sender, pk=['vin']) \
            .where("date_format(created_at, 'yyyyMMdd') = '20220101'") \
            .where("`vin` = 'fakevin'")

# intersect difference compare, PairResult 객체 반환
pair_result = PandasValidator.difference_compare(source=source, target=target)
```

#### PairResult 결과

```plain
[TIME ELAPSED] - (time: 0:00:00.063220, text: difference compare)
(source:                    
                   vin   location
0    19UUA56763A081084  left_only
1    19UUA65545A837147  left_only
..                 ...        ...
998  YV4902NC9F1050126  left_only
999  YV4952BL9E1397234  left_only

[1000 rows x 2 columns], 

target:                     
                    vin    location
1000  19UUA65684A456148  right_only
1001  19UUA66228A764918  right_only
...                 ...         ...
1848  YV4952CF4C1496548  right_only
1849  ZHWGU5BR6EL855505  right_only

[850 rows x 2 columns], 
match: False)
```

### 테이블간의 불일치 데이터 추출 

#### MariaDB(or MySQL) to Apache Hive

```python
from migcomparator.models.pandas_validator import PandasValidator
from migcomparator.models.table import Table, ColumnPair
from migcomparator.query_sender.connector import MariadbConnector, HiveConnector

...

# create source & target logical table
source = Table(name='mock_1', sender=mariadb_sender) \
            .where("date_format(`created_at`, '%Y%m%d') = '20220101'") \
            .where("`vin` = 'fakevin'")

# Hive 테이블은 pk를 명시적으로 지정
target = Table(name='mock_3', sender=hive_sender, pk=['vin']) \
            .where("date_format(created_at, 'yyyyMMdd') = '20220101'") \
            .where("`vin` = 'fakevin'")

# SingleResult 객체 반환
single_result = PandasValidator.value_compare(
            source=source,
            target=target,
            # on은 join대상의 컬럼을 명시적으로 지정, 이름이 같다면 생략가능
            on=[ColumnPair(source='vin', target='vin')],
            # colpair는 테이블간의 컬럼명이 다를때 매치시키기 위해 사용
            colpair=[
                ColumnPair(source='car_make', target='car_mk'),
                ColumnPair(source='car_model_year', target='car_model_yyyy'),
                ColumnPair(source='num', target='numb'),
            ])
```

#### SingleResult 결과

- 일치하는 데이터는 `None`, 불일치하는 데이터는 `[source value, target value]` 형식으로 구성 

```plain
[TIME ELAPSED] - (time: 0:00:00.085695, text: value compare)
               vin,vin                      color,color          num,numb
0    19UUA56763A081084  [Goldenrod, GoldenrodGoldenrod]  [57.064, 58.064]
1    19UUA65545A837147           [Yellow, YellowYellow]              None
2    19UUA65566A654351           [Orange, OrangeOrange]              None
3    19UUA76537A154797           [Fuscia, FusciaFuscia]    [6.472, 7.472]
4    19UUA76667A986661  [Turquoise, TurquoiseTurquoise]  [40.263, 41.263]
..                 ...                              ...               ...
995  YV440MBC6F1570276                 [Teal, TealTeal]      [35.4, 36.4]
996  YV440MBD6F1653487           [Yellow, YellowYellow]  [81.213, 82.213]
997  YV4852CZ6B1343304                 [Blue, BlueBlue]  [31.325, 32.325]
998  YV4902NC9F1050126  [Turquoise, TurquoiseTurquoise]  [34.464, 35.464]
999  YV4952BL9E1397234  [Goldenrod, GoldenrodGoldenrod]  [98.871, 99.871]
```

## User Component

### Connector

DataSource에게 질의를 수행하고 결과를 Validator에게 전달해주기위한 클래스.
- `MariadbConnector`
- `HiveConnector`

```python
from migcomparator.query_sender.connector import MariadbConnector, HiveConnector

mariadb_sender = \ 
        MariadbConnector(
            host='localhost',
            port=3306,
            user='username',
            password='password',
            database='schema'
        )

hive_sender = \ 
        HiveConnector(
            host='localhost',
            port=10000,
            user='username',
            password='password',
            database='schema',
            auth_mechanism='PLAIN'
        )
```



---

### Table

```python
from migcomparator.models.table import Table

source = Table(name='mock_1', sender=mariadb_sender) \
            .where("date_format(`created_at`, '%Y%m%d') = '20220101'")

# Hive 테이블은 pk를 명시적으로 지정
target = Table(name='mock_2', sender=hive_sender, pk=['vin']) \
            .where("date_format(created_at, 'yyyyMMdd') = '20220101'")
```

```python
__init__(self, name: str, sender: BaseConnectorMeta, pk: List[str]): Table
```

- **name** 
  - DataSource에 위치한 테이블명
- **sender** 
  - 사용할 Connector객체를 기입 (`MariadbConnector` or `HiveConnector`)
- **pk**
  - Hive에 위치한 테이블의 경우 pk를 명시적으로 기입

```python
where(self, clause: str): Table
```

- **clause**
  - 테이블에서 데이터를 필터링하기위한 where 구문

---

### ColumnPair

```python
from migcomparator.models.table import ColumnPair

colpair = ColumnPair(source='car_model_year', target='car_model_yyyy')
```

```python
__init__(self, source: str, target: str): Table
```
 
비교하고자 하는 테이블간의 컬렴밍이 다른경우 컬럼명을 매치시키기 위해 사용
- **source**
  - source 테이블의 컬럼명
- **target**
  - target 테이블의 컬럼명

---

### Validator

- `PandasValidator` 
  - DataSource에 위치한 데이터를 라이브러리가 설치된 단일머신으로 들고와 비교를 수행하는 Validator (소규모 데이터셋에 적합)

#### 데이터 건수 비교

```python
count_compare(cls, source: Table, target: Table): PairResult
```

source와 target에 비교대상 `Table` 객체를 인자로 전달하여, 두 테이블간의 데이터 count 결과반환


#### 대칭차집합 비교

```python
difference_compare(cls, source: Table, target: Table, colpair: List[ColumnPair] = None): PairResult
```

source와 target에 비교대상 `Table` 객체를 인자로 전달하여, full-outer join 수행후,
각 테이블에 존재하지 않는 primary key를 반환

- **colpair**
  - 비교하고자 하는 테이블간의 컬렴밍이 다른경우 컬럼명을 매치시키기 위해 사용


#### 테이블간의 불일치 데이터 추출

```python
value_compare(cls, source: Table, target: Table, on: List[ColumnPair] = None, colpair: List[ColumnPair] = None): SingleResult
```


source와 target에 비교대상 `Table` 객체를 인자로 전달하여, inner join후, 테이블의 모든 컬럼들을 비교하여 불일치하는 데이터 추출

- **on**
  - inner join의 대상이되는 컬럼들을 명시적으로 지정할때 사용(pk의 컬럼명이 다른경우 사용)
- **colpair**
  - 비교하고자 하는 테이블간의 컬렴밍이 다른경우 컬럼명을 매치시키기 위해 사용