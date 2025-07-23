import math

class Paginator:
    def __init__(self, array: list, per_page:int, page: int = 1):
        self.array = array
        self.pages = math.ceil(len(array)/per_page)
        self.per_page = per_page
        self.page = page

    def __get_slice(self):
        start = (self.page - 1)*self.per_page
        end = start + self.per_page
        return self.array[start: end]

    def has_next(self):
        if self.page < self.pages:
            return self.page
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_first(self):
        return self.__get_slice()

    def get_next(self):
        if self.page <= self.pages:
            return self.__get_slice()
        raise IndexError(f'Next page does not exist. Use has_next() to check before.')

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError(f'Previous page does not exist. Use has_previous() to check before.')