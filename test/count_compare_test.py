#!/bin/bash/env python

from unittest import TestCase, main

from models.validation_result import PairResult
from models.pandas_validator import PandasValidator
from models.table import Table
from query_sender.connector import MariadbConnector


class CountCompareTest(TestCase):

    def test_count_rdb_to_rdb(self):
        # given
        sender = MariadbConnector(
            host='localhost',
            port=3307,
            user='scott',
            password='tiger',
            database='temporary'
        )
        source = Table(name='mock_1', sender=sender)\
            #.where("date_format(created_at, '%Y%m%d') = '20210714'")

        target = Table(name='mock_2', sender=sender) \
            #.where("date_format(created_at, '%Y%m%d') = '20210714'")

        # when & then
        assert PandasValidator.count_compare(source=source, target=target) \
               == PairResult(1000, 850, False)


if __name__ == '__main__':
    main()
