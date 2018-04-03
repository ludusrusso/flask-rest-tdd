class FakeDB(object):
    def __init__(self):
        self._db = {}

    def add_user(self, username, password, data={}):
        data["username"]=username
        self._db[username] = (password, data)

    def get_user(self, username):
        return self._db[username][1]

    def check_user(self, username, password):
        try:
            return self._db[username][0] == password
        except KeyError:
            return False
