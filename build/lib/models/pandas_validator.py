from typing import List

import pandas as pd

from common.commonutils import elapsed_time
from models.base_validator import ValidatorMeta
from models.table import Table, ColumnPair, Column
from models.validation_result import PairResult, SingleResult

PAIR = (0, 1)
SOURCE, TARGET = PAIR

INDICATOR = 'location'
INDICATOR_MAP = {
    SOURCE: 'left_only',
    TARGET: 'right_only'
}


class PandasValidator(ValidatorMeta):
    @classmethod
    @elapsed_time("count compare")
    def count_compare(cls, source: Table, target: Table) -> PairResult:
        """
        테이블간 건수비교 수행
        :param source: source table
        :param target: target table
        :return:
        """
        plain_table = [source, target]
        table = [ValidatorMeta.generate(plain_table[_]) for _ in PAIR]

        # count 수행
        result = [table[_].count() for _ in PAIR]

        return PairResult(
            source=result[SOURCE],
            target=result[TARGET],
            # source와 target의 건수가 일치하는가? 일치하면 참
            match=result[SOURCE] == result[TARGET]
        )

    @classmethod
    @elapsed_time("difference compare")
    def difference_compare(cls, source: Table, target: Table, colpair: List['ColumnPair'] = None) -> PairResult:
        """
        pk 기준으로 대칭차집합이 발생하는 row들을 조회
        :param colpair:
        :param source:
        :param target:
        :return:
        """
        plain_table = [source, target]
        table = [ValidatorMeta.generate(plain_table[_]) for _ in PAIR]

        # left_on, right_on에 사용할 컬럼(조인의 대상 컬럼)들 사전순 정렬
        pk = [[col for col in table[_].primary_key] for _ in PAIR]
        pk = [sorted(pk[_], key=lambda c: c.name) for _ in PAIR]

        pk[SOURCE], pk[TARGET], _ = ColumnPair.sorted(
            source=pk[SOURCE],
            target=pk[TARGET],
            pair_list=colpair
        )

        # select한 결과를 DF로 생성
        df = [table[_].select(pk[_]) for _ in PAIR]

        # full outer join 수행
        outer_df = \
            pd.merge(df[SOURCE],
                     df[TARGET],
                     how='outer',
                     left_on=Column.flat(pk[SOURCE]),
                     right_on=Column.flat(pk[TARGET]),
                     indicator=INDICATOR)

        # outer_df에서 left_only, right_only 분리하여 두개의 DF로
        result_df = [outer_df.query(f"{INDICATOR} == '{INDICATOR_MAP[_]}'") for _ in PAIR]

        return PairResult(
            source=result_df[SOURCE],
            target=result_df[TARGET],
            # left_only, target_only 모두 0건인경우 대칭차집합이 발생하지 않으므로 참
            match=len(result_df[SOURCE]) == 0 and len(result_df[TARGET]) == 0
        )

    @classmethod
    @elapsed_time("value compare")
    def value_compare(cls, source: 'Table', target: 'Table', colpair: 'ColumnPair' = None) -> SingleResult:
        """
        테이블의 모든값 비교
        :param source:
        :param target:
        :param colpair:
        :return:
        """
        plain_table = [source, target]
        table = [ValidatorMeta.generate(plain_table[_]) for _ in PAIR]

        # left_on, right_on에 사용할 컬럼(조인의 대상 컬럼, 비교대상 컬럼)들 사전순 정렬
        pk = [[col for col in table[_].primary_key] for _ in PAIR]
        pk = [sorted(pk[_], key=lambda c: c.name) for _ in PAIR]
        col = [[col for col in table[_].columns] for _ in PAIR]
        col = [sorted(col[_], key=lambda c: c.name) for _ in PAIR]

        # 테이블간 컬럼명이 다른경우 colpair에 맞게 재정렬
        pk[SOURCE], pk[TARGET], _ = \
            ColumnPair.sorted(
            source=pk[SOURCE],
            target=pk[TARGET],
            pair_list=colpair)
        col[SOURCE], col[TARGET], dup = \
            ColumnPair.sorted(
            source=col[SOURCE],
            target=col[TARGET],
            pair_list=colpair)

        # select한 결과를 DF로 생성
        df = [table[_].select(pk[_] + col[_]) for _ in PAIR]

        # inner join 수행
        inner_df = \
            pd.merge(df[SOURCE],
                     df[TARGET],
                     how='inner',
                     left_on=Column.flat(pk[SOURCE]),
                     right_on=Column.flat(pk[TARGET]),
                     indicator=INDICATOR)

        pk_names = [pk_name for pk_name in Column.flat(pk[SOURCE])]
        suffix = ['_x', '_y']
        result_df = inner_df[pk_names]
        result_df.columns = [','.join([pk_name, pk[TARGET][i].name]) for i, pk_name in enumerate(pk_names)]
        match = True
        for col_no, _ in enumerate(col[SOURCE]):
            # source와 target에 colname이 공통으로 존재하면 suffix가 붙고,
            # 공통이 아니면 suffix가 안붙는다.
            colname = lambda which, idx: \
                (col[which][idx].name + suffix[which]) \
                if col[which][idx].name in dup \
                else col[which][idx].name

            # pandas series를 numpy로 변환
            np_arr = [inner_df[colname(_, col_no)].to_numpy() for _ in PAIR]
            # bool list
            compare_result = np_arr[SOURCE] == np_arr[TARGET]
            # False인것들의 row_no만 획득

            row = []
            for row_no, result in enumerate(compare_result):
                # True면 NaN
                if result:
                    row.append(None)
                # False면 [source value, target value]
                else:
                    match = False
                    value_pair = [inner_df.loc[row_no, colname(_, col_no)] for _ in PAIR]
                    row.append(value_pair)

            result_df = \
                pd.concat([result_df,
                           pd.Series(row, name=','.join([col[_][col_no].name for _ in PAIR]))], axis=1)

        return SingleResult(result_df, match)
