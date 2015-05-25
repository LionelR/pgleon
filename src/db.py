
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

class DBError:
    def __init__(self, msg):
        """Used to push messages to the UI
        """
        self.msg = msg

    def get_msg(self):
        return self.msg


class Database(object):
    def __init__(self, id, name, host, port, database, user, password):
        self.id = id # id of the connection pool
        self.name = name
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def newConnection(self):
        connection = psycopg2.connect(host=self.host,
                                      port=self.port,
                                      database=self.database,
                                      user=self.user,
                                      password=self.password)
        connection.autocommit = True
        return connection

    def execute(self, query, connection=None, size=None):
        oneShot = False
        if connection is None:
            connection = self.newConnection()
            oneShot = True
        cursor = connection.cursor()
        try:
            cursor.execute(query)
        except Exception as e:
            connection.rollback()
            return None, DBError(e.__str__()), None
        if cursor.description is not None:
            headers = [c[0] for c in cursor.description]
        else:
            headers = list()
        res = self.fetch(cursor, size)
        status = cursor.statusmessage
        cursor.close()
        if oneShot:
            connection.close()
        return headers, res, status

    def fetch(self, cursor, size=None):
        try:
            if size:
                return cursor.fetchmany(size)
            else:
                return cursor.fetchall()
        except psycopg2.ProgrammingError, err:
            return DBError(err)
