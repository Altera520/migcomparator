#!/bin/bash/env python

from unittest import TestCase, main

from migcomparator.models.pandas_validator import PandasValidator
from migcomparator.models.table import Table, ColumnPair
from migcomparator.query_sender.connector import MariadbConnector


class ValueCompareTest(TestCase):

    def test_value_compare_rdb_to_rdb(self):
        # given
        sender = MariadbConnector(
            host='localhost',
            port=3307,
            user='scott',
            password='tiger',
            database='temporary'
        )
        source = Table(name='mock_1', sender=sender, columns=['vin', 'color', 'num'])
        target = Table(name='mock_3', sender=sender, columns=['vin', 'color', 'numb'])

        # when & then
        single_result = PandasValidator.value_compare(
            source=source,
            target=target,
            # on은 join대상의 컬럼을 명시적으로 지정, 이름이 같다면 생략가능
            on=[ColumnPair(source='vin', target='vin')],
            colpair=[
                ColumnPair(source='car_make', target='car_mk'),
                ColumnPair(source='car_model_year', target='car_model_yyyy'),
                ColumnPair(source='num', target='numb'),
            ])

        cell = single_result.result.loc[0, 'num,numb']
        assert cell == [57.064, 58.064]


if __name__ == '__main__':
    main()
