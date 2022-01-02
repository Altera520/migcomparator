import re
from typing import List, Callable, Tuple

from pandas import DataFrame

from migcomparator.common.stringutils import EMPTY, strip_margin, escape
from migcomparator.models.table import Table, Column
from migcomparator.models.typeconverter import TypeConverter
from migcomparator.query_sender.decorator import sendquery
import pandas as pd


class DataSourceTable:
    col_pattern = re.compile('[a-zA-Z0-9_]*')

    def __init__(
            self,
            table: Table
    ) -> None:
        """
        Validation시 Table 클래스를 바탕으로 생성되는 클래스

        :param table: Table
        """
        self._table = table
        self._where = table.mkstring_where()
        self._primary_key, self._columns = DataSourceTable.parse(self, table.pk)

    @property
    def name(self):
        return self._table.name

    @property
    def sender(self):
        return self._table.sender

    @property
    def where(self):
        return self._where

    @property
    def primary_key(self):
        return self._primary_key

    @property
    def columns(self):
        return self._columns

    @sendquery()
    def describe(self) -> str:
        """
        테이블의 정보를 describe

        :return:
        """
        query = strip_margin(f"""
                | desc {escape(self.name)}
                """)
        return query

    @sendquery(form=lambda r: r[0][0])
    def count(self) -> str:
        """
        데이터 건수 반환

        :return:
        """
        query = strip_margin(f"""
                | select count(*)
                |   from {escape(self.name)}
                |  where {self.where} 
                """)
        return query

    def select(self, columns: List[Column], form: Callable = None) -> DataFrame:
        """
        테이블에서 컬럼들 조회하여 pandas DF로 반환

        :param columns: Column 리스트
        :param form:
        :return:
        """
        cols = [col.name for col in columns]

        @sendquery(form=form)
        # TODO: sender 파라미터를 기입안하게끔 데코레이터 수정필요
        def select_inner(sender):
            return strip_margin(f"""
                    | select {', '.join(map(escape, cols))}
                    |   from {escape(self.name)}
                    |  where {self.where} 
                    """)

        df = TypeConverter.convert_type(pd.DataFrame(select_inner(self)), columns, self.sender)
        return df

    @classmethod
    def parse(cls, table: 'DataSourceTable', pk: List[str] = None) -> Tuple[List[Column], List[Column]]:
        """
        describe 쿼리를 통해 테이블 컬럼별 정보 정형화
        :param pk:
        :param table:
        :return:
        """
        desc_raw_result = table.describe()
        result = {
            'primary_key': [],
            'columns': []
        }

        # column list to dict
        temp = {}
        for column in table._table.columns:
            temp[column] = None

        # Hive 테이블은 PK가 없으므로 명시적으로 기입해야한다.
        if pk is not None:
            pk_dict = {}
            for colname in pk:
                pk_dict[colname] = 'PRI'
            for row in desc_raw_result:
                colname = row[0]
                row.append(pk_dict[colname] if colname in pk_dict else '')

        for row in desc_raw_result:
            colname = row[0]

            # Table 객체를 생성할때 기입했던 컬럼만 포함시킨다.
            if '*' not in temp and colname not in temp:
                continue

            # PRI, MUL이면 pk에 등록, 아니면 col에 등록
            field = result['primary_key'] if row[3] in ['PRI', 'MUL'] else result['columns']

            if colname != EMPTY and cls.col_pattern.match(colname):
                # column name, column type
                field.append(Column(colname, row[1]))
        return result['primary_key'], result['columns']
