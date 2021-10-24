from migvalidator.mapper.default_mapper import DefaultMapper
from migvalidator.mapper.default_mapper import query
from impala.dbapi import connect


class HiveMapper(DefaultMapper):
    def __init__(self, host, port, user, password, database, **kwargs):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._kwargs = kwargs

    def get_conn(self, **kwargs):
        return connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db=self._database,
            **self._kwargs
        )

    @query(form=DefaultMapper._describe, log=False)
    def describe(self, table_name):
        return super().describe(table_name)

    @query(form=DefaultMapper._count)
    def count(self, tbl, where):
        return super().count(tbl, where)

    @query()
    def select_all(self, tbl, where):
        return super().select_all(tbl, where)

    @query()
    def select_pk_group(self, tbl, where):
        return super().select_pk_group(tbl, where)

    '''hive 전용 쿼리, hive에서는 엔티티 무결성이 발생하지 않으므로 이를 식별하기 위함'''
    @query()
    def duplicate(self, tbl, where):
        pk_quote = DefaultMapper.add_quote_to_string(tbl.pk)
        table_quote = DefaultMapper.add_quote(tbl.table)

        q = f"""
            select {pk_quote} 
                from ( 
                    select {pk_quote}, count(*) as `cnt`
                      from {table_quote}
                      {str(where)}
                     group by {pk_quote}
                ) t1
               where 1 = 1
                 and `cnt` <> 1  
        """
        return q


