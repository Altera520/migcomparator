from abc import *


class query(object):
    '''데코레이터에 인자 설정'''
    def __init__(self, form=None, log=True):
        self.form = form
        self.log = log

    '''실제 데코레이터'''
    def __call__(self, create_sql):
        def wrap(mapper, *args):
            sql = create_sql(mapper, *args)
            if self.log:
                query.print_sql(sql, mapper)
            raw_result = self.send_sql(mapper.get_conn(), sql)
            return self.form(raw_result) if self.form else raw_result
        return wrap

    '''data source에 쿼리문 전송'''
    def send_sql(self, conn, sql):
        cursor = conn.cursor()
        cursor.execute(sql)
        res = list(cursor.fetchall())
        cursor.close()
        conn.close()

        # 문자열 디코딩 처리
        for idx, row in enumerate(res):
            res[idx] = tuple(v.decode('utf-8') if isinstance(v, bytes) else v for v in row)
        return res

    '''sql문 출력'''
    @classmethod
    def print_sql(cls, sql, mapper):
        # TODO: ip를 찍어주는것이 바람직한가?
        print(f"""[SEND QUERY] -\n (target: {mapper.host}""", end='')
        query_text = ' '.join([line.strip() for line in sql.splitlines()]).strip()
        print(f""",\n  query: {query_text})""")


class DefaultMapper(metaclass=ABCMeta):

    @property
    def host(self):
        return self._host

    @abstractmethod
    def get_conn(self):
        pass

    @abstractmethod
    def describe(self, table_name):
        return f"desc {DefaultMapper.add_quote(table_name)}"

    @abstractmethod
    def count(self, tbl, where):
        table_quote = DefaultMapper.add_quote(tbl.table)
        sql = f"""
            select count(*) 
              from {table_quote}
            {str(where)}
        """
        return sql

    @abstractmethod
    def select_pk_group(self, tbl, where):
        pk_quote = DefaultMapper.add_quote_to_string(tbl.pk)
        table_quote = DefaultMapper.add_quote(tbl.table)
        sql = f"""
            select {pk_quote}
              from {table_quote} 
            {str(where)}  
        """
        return sql

    @abstractmethod
    def select_all(self, tbl, where):
        col_quote = DefaultMapper.add_quote_to_string(tbl.pk + tbl.col)
        table_quote = DefaultMapper.add_quote(tbl.table)
        sql = f"""
            select {col_quote}
              from {table_quote} 
            {str(where)}
        """
        return sql

    @classmethod
    def add_quote_to_string(cls, col):
        return ', '.join([DefaultMapper.add_quote(_) for _ in col])

    @classmethod
    def add_quote(cls, identifier):
        quote = '`'
        return ''.join([quote, identifier, quote])

    '''table describe raw 데이터를 정형화'''
    @classmethod
    def _describe(cls, result):
        def get_type(raw_type):
            # TODO: 타입 정형화하는 부분은 수정 필요
            type_split = raw_type.split('(')
            p_s = [None, None]
            if len(type_split) == 2:
                for idx, _ in enumerate(type_split[1].replace(')', '').split(',').map(int)):
                    p_s[idx] = _
            return {
                'type': type_split[0],
                'p': p_s[0],
                's': p_s[1]
            }

        '''
        "pk": [],
        "col": [],
        "info": {
            <column_name>: {
                "type": string,
                "p": None or Int, optional
                "s": None or Int, optional
            }
        }
        '''
        meta = {
            "pk": [],
            "col": [],
            "info": {}
        }
        for row in result:
            meta_ = meta['pk'] if row[3] in ['PRI', 'MUL'] else meta['col']
            col_name = row[0]
            meta_.append(col_name)
            meta['info'][col_name] = get_type(row[3])
        return meta

    @classmethod
    def _count(cls, result):
        return result[0][0]
