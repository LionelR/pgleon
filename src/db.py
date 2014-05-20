__author__ = 'lionel'

import psycopg2


class DBError:
    def __init__(self, msg):
        """Used to push messages to the UI
        """
        self.msg = msg

    def get_msg(self):
        return self.msg


class Database(object):
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        # host = "localhost"
        # port = "5432"
        # database = "booktown"
        # user = "lionel"
        # password = "lionel"
        self.connect()

    def connect(self):
        self.conn = psycopg2.connect(host=self.host,
                                     port=self.port,
                                     database=self.database,
                                     user=self.user,
                                     password=self.password)
        self.cur = self.conn.cursor()

    def execute(self, query, size=None):
        try:
            self.cur.execute(query)
        except Exception as e:
            return None, DBError(e.__str__())
        headers = [c.name for c in self.cur.description]
        res = self.fetch(self.cur, size)
        return headers, res

    def fetch(self, cur, size=None):
        try:
            if size:
                return cur.fetchmany(size)
            else:
                return cur.fetchall()
        except psycopg2.ProgrammingError, err:
            return DBError(err)

    def close(self):
        self.cur.close()
        self.conn.close()


