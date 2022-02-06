class Output:
    def __init__(self):
        self._indexes = []

    def add_index(self, index):
        self._indexes.append(index)

    def get_indexes(self):
        return self._indexes

    def get_number(self):
        return len(self._indexes)
