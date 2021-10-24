import numpy
import pandas as pd
import numpy as np
from datetime import datetime

from migvalidator.component.result import Result
from migvalidator.component.where import Where

SOURCE = 0
TARGET = 1
INDICATOR = 'location'
INDICATOR_MAP = {
    'left_only': 'source',
    'right_only': 'target'
}

TYPE_MAP = {
    'char': str,
    'varchar': str,
    'tinytext': str,
    'text': str,
    'mediumtext': str,
    'longtext': str,
    'binary': str,
    'varbinary': str,
    'date': str,
    'datetime': str,
    'timestamp': str,
    'time': str,
    'tinyint': np.byte,
    'smallint': np.short,
    'mediumint': np.intc,
    'int': np.intc,
    'integer': np.int,
    'bigint': np.int_,
    'decimal': np.double,
    'dec': np.double,
    'numeric': np.double,
    'fixed': np.double,
    'float': np.float,
    'double': np.double,
    'bool': np.bool,
    'boolean': np.bool,
    '_': str                # default
}


class elapsed_time:
    def __init__(self, text=None):
        self._text = f', text: {text})' if text else ')'

    '''경과시간 출력 데코레이터'''
    def __call__(self, func):
        def wrap(instance, *args, **kwargs):
            start_time = datetime.now()
            result = func(instance, *args, **kwargs)
            end_time = datetime.now()
            print(f"[TIME ELAPSED] - (time: {end_time - start_time}{self._text}")
            return result
        return wrap


# TODO: Goal. 초대용량 데이터에 대해서도 전수검사를 실시할 수 있는 라이브러리를 만드는게 목표
class Validator:
    def __init__(self, source, target, rule):
        # TODO: 컬럼명에 rule 반영해서 일치하는지 여부도 체크해야
        if len(source.col) != len(target.col):      # 컬럼 갯수가 일치하지 않으면 에러
            raise AttributeError
        self._table = [source, target]
        self._rule = rule

    @property
    def table(self):
        return self._table

    @property
    def rule(self):
        return self._rule

    '''dataframe 타입 변환'''
    def __df_type_convert(self, df, info, col):
        for idx, _ in enumerate(df):
            type = info[col[idx]]['type']
            type = type if type in TYPE_MAP else TYPE_MAP['_']
            df[_] = df[_].astype(type, errors='ignore')
            print(df[_].dtypes)
        return df

    '''테이블의 row 건수가 같은가?'''
    @elapsed_time('count comparison')
    def count_comparison(self, source=Where(), target=Where(), common=Where()):
        where = Where.distribute(source, target, common)
        count = [
            self.table[_].mapper.count(
                self.table[_],
                where[_]
            )
            for _ in range(2)
        ]
        return Result(
            source=(count[SOURCE],),
            target=(count[TARGET],),
            match=count[SOURCE] == count[TARGET]
        )

    '''source, target에서 대칭차집합이 발생하지 않는가?'''
    @elapsed_time('row comparison')
    def row_comparison(self, source=Where(), target=Where(), common=Where()):
        '''outer join 수행'''
        def outer_join(df, col):
            outer_df = pd.merge(
                df[SOURCE],
                df[TARGET],
                how='outer',
                indicator=INDICATOR
            )
            intersect_count = len(outer_df.index)
            outer_df[INDICATOR] = outer_df[INDICATOR].map(INDICATOR_MAP)
            outer_df = [
                outer_df.query(f"{INDICATOR} == '{_}'")
                for _ in INDICATOR_MAP.values()
            ]
            outer_df[SOURCE].columns = col[SOURCE] + [INDICATOR]
            outer_df[TARGET].columns = col[TARGET] + [INDICATOR]
            return outer_df, intersect_count

        '''join 결과가 옳은지 검사'''
        def is_reliable(df, count, intersect_count):
            f = lambda _: len(df[_].index) == count[_] + intersect_count
            return f(SOURCE) and f(TARGET)

        where = Where.distribute(source, target, common)
        tmp_col = [idx for idx in range(len(self.table[SOURCE].pk))]  # 임시컬렴명
        df = [
            self.__df_type_convert(
                pd.DataFrame(  # TODO: dataframe의 타입을 한번 정리해줘야한다. 값에 대한 가공을 외부에서 주입할수 있어야한다.
                    # TODO: pk에 rule을 적용해서 순서를 맞춰야 한다.
                    self.table[_].mapper.select_pk_group(
                        self.table[_],
                        where[_]
                    ),
                    columns=tmp_col  # empty인 경우를 대비해서 임시컬렴명을 명시적으로 부여
                ),
                self.table[_].info,
                self.table[_].pk
            )
            for _ in range(2)
        ]

        outer_df, intersect_count = outer_join(df, [self.table[SOURCE].pk, self.table[TARGET].pk])
        count = len(outer_df[SOURCE].index), len(outer_df[TARGET].index)

        if not is_reliable(df, count, intersect_count):
            raise AttributeError        # TODO: AttributeError대신 다른 에러로 교체필요

        return Result(
            source=(outer_df[SOURCE], count[SOURCE]),
            target=(outer_df[TARGET], count[TARGET]),
            additional=(intersect_count,),
            match=(count[SOURCE] + count[TARGET]) == 0
        )

    '''대용량 테이블의 경우, 모든 row를 비교하는 것은 무리가 있으므로, numeric 타입에 대한 sum 비교'''
    def sum_diff(self):
        pass

    '''대용량 테이블의 경우, 모든 row를 비교하는 것은 무리가 있으므로, order by하여 구간별 샘플링해서 비교'''
    def order_diff(self):
        pass

    '''대용량 테이블의 경우, 모든 row를 비교하는 것은 무리가 있으므로, min, max 값을 통한 비교'''
    def min_max_diff(self):
        pass

    '''source, target의 모든 컬럼값 매치하는지 비교'''
    @elapsed_time('value comparison')
    def value_comparison(self, source=Where(), target=Where(), common=Where()):
        where = Where.distribute(source, target, common)
        tmp_pk = [_ for _ in range(len(self.table[SOURCE].pk))]                      # 임시 pk명
        pk_len = len(tmp_pk)
        tmp_col = [_ for _ in range(pk_len, len(self.table[SOURCE].col) + pk_len)]   # 임시 컬럼명
        # TODO: Rule순서에 따라서 컬럼간 비교 로직 필요
        df = [
            self.__df_type_convert(
                # TODO: col에 rule을 적용해서 순서를 맞춰야 한다.
                pd.DataFrame(  # TODO: dataframe의 타입을 한번 정리해줘야한다. 값에 대한 가공을 외부에서 주입할수 있어야한다.
                    self.table[_].mapper.select_all(
                        self.table[_],
                        where[_]
                    ),
                    columns=tmp_pk + tmp_col  # empty인 경우를 대비해서 임시컬렴명을 명시적으로 부여
                ),
                self.table[_].info,
                self.table[_].pk + self.table[_].col
            )
            for _ in range(2)
        ]
        # TODO: pk 컬럼에 대해 타입을 맞추어야한다.
        inner_df = pd.merge(df[SOURCE], df[TARGET], how='inner', on=tmp_pk)
        join_col = [(f'{_}_x', f'{_}_y') for _ in tmp_col]
        unmatched_map = {}
        unmatched_count = 0
        for col_no, col_name in enumerate(join_col):
            np = [inner_df[col_name[_]].to_numpy() for _ in range(2)]
            result = np[SOURCE] == np[TARGET]
            result = [row_no for row_no, _ in enumerate(result) if not _]
            unmatched_count += len(result)
            col_name = self.table[SOURCE].col[col_no], self.table[TARGET].col[col_no]

            for _ in range(2):
                unmatched_map[col_name[_]] = result

        return Result(
            additional=(inner_df, unmatched_map, unmatched_count),
            match=unmatched_count == 0
        )

    '''source, target 비교없이 target 단독으로 검증하는경우 사용'''
    @elapsed_time("single validation")
    def apply(self, func, tbl, where=Where(), validation=None, form=None):
        result = func(tbl, where)
        if form:
            result = form(result)
        is_match = validation(result) if validation else None

        return Result(
            target=(result, ),
            match=is_match
        )
