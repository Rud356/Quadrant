class MemoreExceptions(Exception):

    class UnexistingObject(Exception):
        pass

class virtual_db:
    __slots__ = '__users', '__objects', '__servers', '__channels', '__messages'
    def __init__(self):
        self.__users = []
        self.__objects = []
        self.__servers = []
        self.__channels = []
        self.__messages = []

    def get_object(self, id: int) -> object:
        try: return self.__objects[int(id)]
        except IndexError: return None
        except ValueError: return None

    def get_message(self, id: int):
        return self.get_object(id)

    def post_message(self, message):
        #TODO: Add validations
        self.__objects.append(
            self.__messages.__add__([message])
        )

class database:
    def __init__(self, virtual=False): pass


class sample_msg:
    def __init__(self, text):
        self.text = text
vdb = virtual_db()
vdb.post_message(sample_msg('hello'))
vdb.post_message(sample_msg('world!'))
vdb.post_message(sample_msg('rud is here!'))
print(vdb.get_message(0))