class Rule:
    '''explicit는 명시적으로 매칭시킬 컬럼 to 컬럼, name_match는 동일한 이름의 컬럼간 매치'''
    def __init__(self, explicit=[], name_match=True):
        self.source = {}
        self.target = {}
        self.name_match = name_match
        for source_col, target_col in explicit:
            self.add(source_col, target_col)

    def __contains__(self, col_name):
        return False if self.get(col_name) is None else True

    def append(self, source_col, target_col):
        self.source[source_col] = target_col
        self.target[source_col] = target_col

    def get(self, from_col_name):
        get_col = lambda dict, col_name, res: dict[col_name] if col_name in dict else res
        to_col_name = get_col(self.source, from_col_name, None)
        return get_col(self.target, from_col_name, to_col_name)

    # TODO: Rule의 remove 구현해야함
    def remove(self, col_name):
        pass
        #if col_name in self:
        #    del self.source[self.get(col_name)]