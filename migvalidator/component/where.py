class Where:
    def __init__(self, *args):
        self.where = list(args)

    def __bool__(self):
        return len(self.where) > 0

    def __str__(self):
        if not self:
            return ''
        return ''.join(['where ', ' and '.join(self.where)])

    @property
    def where(self):
        return self._where

    @where.setter
    def where(self, where):
        for idx, _ in enumerate(where):
            where[idx] = _.strip()
            if where[idx] == '':         # 공백 문자열은 where이 될수 없다.
                raise AttributeError
        self._where = where

    def append(self, other):
        if other:
            return Where(*(self.where + other.where))    # Where는 불변객체이므로 새로운 Where 생성
        return self

    '''common을 source와 target에 분배'''
    @classmethod
    def distribute(cls, source, target, common):
        return source.append(common), target.append(common)