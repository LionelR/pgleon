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
    def __init__(self):
        host = "localhost"
        database = "booktown"
        user = "lionel"
        password = "lionel"
        self.conn = self.connection(database, user, password, host)
        self.cur = self.conn.cursor()

    def connection(self, database, user, password, host=None):
        return psycopg2.connect(database=database,
                                user=user,
                                password=password,
                                host=host)

    def execute(self, query, size=None):
        self.cur.execute(query)
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


