#!/bin/bash/env python

from unittest import TestCase, main

from models.validation_result import PairResult
from models.pandas_validator import PandasValidator
from models.table import Table
from query_sender.connector import MariadbConnector


class CountCompareTest(TestCase):

    def test_count(self):
        # given
        sender = MariadbConnector(
            host='localhost',
            port=3307,
            user='scott',
            password='tiger',
            database='maasbi'
        )
        source = Table(name='dw_vn_prct_bs', sender=sender)\
            .where("date_format(etl_cre_dtm, '%Y%m%d') = '20210714'")

        target = Table(name='dw_vn_prct_bs', sender=sender) \
            .where("date_format(etl_cre_dtm, '%Y%m%d') = '20210714'")

        # when & then
        assert PandasValidator.count_compare(source=source, target=target) \
               == PairResult(123, 123, True)


if __name__ == '__main__':
    main()
