import logging as log
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from models.datasource_table import DataSourceTable


class sendquery(object):
    def __init__(self, form=None):
        """
        데코레이터 인자 설정

        :param form: fetch한 결과 정형화
        """
        self.form = form

    def __call__(self, create_query: Callable):
        """
        query를 전송하는 데코레이터

        :param create_query:  호출 함수
        :return:
        """
        def wrap(table: 'DataSourceTable', *args):
            query = create_query(table, *args)
            # 쿼리에 질의 수행
            print(query)
            raw_result = self.send_query(table.sender.connect(), query)
            return self.form(raw_result) if self.form else raw_result
        return wrap

    def send_query(self, conn, query: str):
        """
        data source에 쿼리문 전송

        :param conn: datasource와 connection
        :param query: 쿼리스트링
        :return:
        """
        cursor = conn.cursor()
        cursor.execute(query)
        res = list(cursor.fetchall())
        cursor.close()
        conn.close()

        # 문자열 utf-8로 디코딩 처리
        for idx, row in enumerate(res):
            res[idx] = tuple(v.decode('utf-8') if isinstance(v, bytes) else v for v in row)
        return res
