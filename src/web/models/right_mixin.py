class RightMixin:

    @staticmethod
    def _fields_base_write():
        return set()

    @staticmethod
    def _fields_base_read():
        return set(['id'])

    @staticmethod
    def _fields_api_write():
        return set([])

    @staticmethod
    def _fields_api_read():
        return set(['id'])

    @classmethod
    def fields_base_write(cls):
        return cls._fields_base_write()

    @classmethod
    def fields_base_read(cls):
        return cls._fields_base_write().union(cls._fields_base_read())

    @classmethod
    def fields_api_write(cls):
        return cls.fields_base_write().union(cls._fields_api_write())

    @classmethod
    def fields_api_read(cls):
        return cls.fields_base_read().union(cls._fields_api_read())

    def __getitem__(self, key):
        if not hasattr(self, '__dump__'):
            self.__dump__ = {}
        return self.__dump__.get(key)

    def __setitem__(self, key, value):
        if not hasattr(self, '__dump__'):
            self.__dump__ = {}
        self.__dump__[key] = value

    def dump(self, role='admin'):
        if role == 'admin':
            dico = {k: getattr(self, k) for k in self.__table__.columns.keys()}
        elif role == 'api':
            dico = {k: getattr(self, k) for k in self.fields_api_read()}
        else:
            dico = {k: getattr(self, k) for k in self.fields_base_read()}
        if hasattr(self, '__dump__'):
            dico.update(self.__dump__)
        return dico
