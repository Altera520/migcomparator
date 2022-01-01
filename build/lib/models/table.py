from typing import List, Optional, Tuple, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from query_sender.connector import BaseConnectorMeta


class Where:
    def __init__(self, clause):
        """
        :param clause: Table 클래스내에서 사용할 필터구문
        """
        self._clause = clause

    def __str__(self):
        return self._clause


class Table:
    def __init__(
            self,
            name: str,
            sender: 'BaseConnectorMeta',
            pk: List[str] = None,
            columns: List[str] = ['*'],
    ) -> None:
        """
        사용자가 정의하는 테이블 클래스

        :param name: 테이블명
        :param sender: 'hive' | 'mariadb'
        :param pk:
        :param columns: 조회할 대상 컬럼
        """
        self._name = name
        self._sender = sender
        self._columns = columns
        self._where = list()
        self._pk = pk

    @property
    def name(self) -> str:
        return self._name

    @property
    def sender(self) -> str:
        return self._sender

    @property
    def pk(self) -> str:
        return self._pk

    @property
    def columns(self) -> List[str]:
        return self._columns

    def where(self, clause: str):
        self._where.append(clause)
        return self

    def mkstring_where(self):
        return 'and '.join(map(lambda where: str(where), self._where))

    @property
    def query(self) -> str:
        return str(self)


class Column:
    def __init__(self, column_name, column_type):
        self._name = column_name
        self._type, self._range = Column.parse(column_type)

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def range(self) -> Tuple:
        return self._range

    @classmethod
    def parse(cls, column_type: str) -> Tuple[str, Tuple[int, Optional[int]]]:
        result = column_type.split('(')
        if len(result) == 2:
            option = result[1].split(',')
            result[1] = (option[0], option[1]) if len(option) == 2 else (option[0], None)
        else:
            result.append(())
        return result

    @classmethod
    def flat(cls, cols: List['Column']) -> List[str]:
        """
        리스트의 Column을 풀어서 내부 name만 리스트로 하여 반환
        :param cols: Column 리스트
        :return:
        """
        return [col.name for col in cols]


class ColumnPair:
    """
    source와 target 테이블간 컬럼명이 다른경우 사용
    """
    def __init__(self, source: str, target: str):
        self._source = Column(source, None)
        self._target = Column(target, None)

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @classmethod
    def sorted(cls,
               source: List[Column],
               target: List[Column],
               pair_list: List['ColumnPair']) -> Tuple[List[Column], List[Column], Dict[str, bool]]:
        tmp = {}
        # source, target에 공통으로 존재하는 컬럼명
        dup = {}
        source_list = []
        target_list = []
        for col in source:
            tmp[col.name] = True

        for col in target:
            # source에 target의 colname이 있으면
            if col.name in tmp:
                source_list.append(col)
                target_list.append(col)
                dup[col.name] = True

        if pair_list is not None:
            # pair_list중 source 컬럼명들과 일치하는것만 필터링
            for pair in [p for p in pair_list if p.source in tmp]:
                # target 컬럼명이 source 컬럼명들과 불일치하는것들 추가
                if pair.target not in tmp:
                    source_list.append(pair.source)
                    target_list.append(pair.target)

        return source_list, target_list, dup
