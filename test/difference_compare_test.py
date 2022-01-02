#!/bin/bash/env python

from unittest import TestCase, main

from migcomparator.models.pandas_validator import PandasValidator
from migcomparator.models.table import Table
from migcomparator.query_sender.connector import MariadbConnector


class DifferenceCompareTest(TestCase):

    def test_difference_rdb_to_rdb(self):
        # given
        sender = MariadbConnector(
            host='localhost',
            port=3307,
            user='scott',
            password='tiger',
            database='temporary'
        )
        source = Table(name='mock_1', sender=sender)
        target = Table(name='mock_2', sender=sender)

        # when & then
        result = PandasValidator.difference_compare(source=source, target=target)

        assert len(result.source) == 1000 and len(result.target) == 850


if __name__ == '__main__':
    main()
