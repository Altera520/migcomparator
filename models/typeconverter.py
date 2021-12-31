from typing import List

import pandera as pa
from pandas import DataFrame

from config.pd_spec_hive import type_map as hive_map
from config.pd_spec_mariadb import type_map as mariadb_map
from models.table import Column
from query_sender.connector import MariadbConnector, HiveConnector, BaseConnectorMeta


class TypeConverter:

    conversion_map = {
        MariadbConnector: mariadb_map,
        HiveConnector: hive_map,
    }

    @classmethod
    def convert_type(cls, df: DataFrame, columns: List[Column], connector: BaseConnectorMeta) -> DataFrame:
        # connector와 col.type에 대응되는 타입으로 스키마에 등록
        schema_dict = {}
        for col in columns:
            # col.name = connector's col.type
            schema_dict[col.name] = pa.Column(
                cls.conversion_map[type(connector)][col.type],
                coerce=True,        # validate를 수행하기전 지정된 dtype으로 변환
                nullable=True       # NaN 허용여부
            )

        schema = pa.DataFrameSchema(
            schema_dict
        )
        df.columns = schema_dict.keys()
        return schema(df)
