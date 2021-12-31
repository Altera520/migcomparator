from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from models.datasource_table import DataSourceTable
from models.table import ColumnPair
from models.validation_result import ValidationResult, SingleResult

if TYPE_CHECKING:
    from models.table import Table


class ValidatorMeta(metaclass=ABCMeta):

    @classmethod
    def generate(cls, table: 'Table') -> DataSourceTable:
        """
        query를 통해 Table 메타데이터를 가지고있는 DataSourceTable 생성
        :param table: Table class
        :return:
        """
        return DataSourceTable(table)

    @classmethod
    @abstractmethod
    def count_compare(
            cls,
            source: 'Table',
            target: 'Table'
    ) -> ValidationResult:
        """
        Table 객체를 통해 count 비교

        :param source: 비교대상 테이블
        :param target: 비교대상 테이블
        :return:
        """
        pass

    @classmethod
    @abstractmethod
    def difference_compare(
            cls,
            source: 'Table',
            target: 'Table',
            colpair: 'ColumnPair' = None
    ) -> ValidationResult:
        """
        source table에 존재하지 않는 target table의 row와
        target table에 존재하지 않는 soruce table의 row를 반환

        :param source: 비교대상 테이블
        :param target: 비교대상 테이블
        :param colpair: table간의 join 대상 컬럼명이 다른경우, colpair를 통해 컬럼 이름 매치
        :return:
        """
        pass

    @classmethod
    @abstractmethod
    def value_compare(
            cls,
            source: 'Table',
            target: 'Table',
            colpair: 'ColumnPair' = None
    ) -> SingleResult:
        """
        source table의 PK를 제외한 컬럼, target table의 PK를 제외한 컬럼들의 모든 값 비교

        :param source: 비교대상 테이블
        :param target: 비교대상 테이블
        :param colpair: table간의 비교 대상 컬럼명이 다른경우, colpair를 통해 컬럼 이름 매치
        :return:
        """
        pass
