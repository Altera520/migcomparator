class Table:
    def __init__(self, table, mapper, col_except=[]):
        def except_filter(meta, col_except):
            return [col for col in meta['col'] if col not in col_except]
        self._table = table
        self._mapper = mapper
        self._meta = mapper.describe(table)
        self._pk = self._meta['pk']
        self._col = except_filter(self._meta, col_except) # except_에 기입된 컬럼은 제외하고 컬럼 describe 생성
        self._info = self._meta['info']

    def __add__(self, other):
        return TableGroup(self, other)

    @property
    def table(self):
        return self._table

    @property
    def mapper(self):
        return self._mapper

    @property
    def meta(self):
        return self._meta

    @property
    def pk(self):
        return self._pk

    @property
    def col(self):
        return self._col

    @property
    def info(self):
        return self._info


class TableGroup:
    def __init__(self, *args):
        self._tables_name = {}
        self._tables_ref = {}
        for tbl in args:
            self._tables_name[tbl.table] = tbl
            self._tables_ref[tbl] = tbl

    def __getitem__(self, item):
        if type(item) == str:
            return self._tables_name[item]
        if type(item) == TableGroup:
            return self._tables_ref[item]
        raise AttributeError
