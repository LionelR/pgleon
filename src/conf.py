#-*- coding:utf-8 -*-

__author__ = 'lionel'

"""
PGLeon.src.conf
Gestion de la partie configuration de pgleon.
"""

import os
import sys
from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, BooleanField, TextField


name = "PGLeon"
version = "0.1"


title = "{0:s}".format(name)

icon_path = 'icons/pgleon.png'


def localFolder():
    if ('win' in sys.platform) and ('darwin' not in sys.platform):
        import winpaths
        lf = os.path.join(winpaths.get_local_appdata(), name)
    else:
        lf = os.path.join(os.path.expanduser('~'), u'.%s'%name.lower())
    if not os.path.exists(lf):
        os.makedirs(lf)
        print("%s created"%lf)
    return lf


dbName = "pgleon.db"
dbPath = os.path.join(localFolder(), dbName)
# os.remove(dbPath)
confDB = SqliteDatabase(dbPath)


class Connection(Model):
    host = CharField(null=True)
    port = CharField(null=True)
    database = CharField(null=True)
    user = CharField(null=True)
    password = CharField(null=True)
    name = CharField(null=False)

    class Meta:
        database = confDB


class Section(Model):
    connection = ForeignKeyField(Connection, related_name='sections')
    name = CharField(null=False)

    class Meta:
        database = confDB


class Query(Model):
    """Queries for one database connection"""
    section = ForeignKeyField(Section, related_name='queries')
    name = CharField(null=False)
    description = CharField()
    query = TextField(null=False)

    class Meta:
        database = confDB


class GlobalQuery(Model):
    """Queries for all databases"""
    name = CharField(null=False)
    description = CharField()
    query = TextField(null=False)

    class Meta:
        database = confDB


Connection.create_table(True)
Section.create_table(True)
Query.create_table(True)
GlobalQuery.create_table(True)



def fixtures():
    """Create defaults items"""
    qList = [["Tables list", "List tables except system ones",
              """SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
AND table_schema NOT IN ('pg_catalog', 'information_schema');"""],
             ["All tables list", "List all tables, including system tables",
              """SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE';"""],
             ["Views list", "List views except system ones",
              """SELECT table_name
FROM information_schema.views
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
AND table_name !~ '^pg_';"""],
             ["All views list", "List all views, including system views",
              """SELECT table_name
FROM information_schema.views;"""]
    ]
    if GlobalQuery.select().count() == 0:
        for name, desc, query in qList:
            sql = GlobalQuery(name=name, description=desc, query=query)
            sql.save()

fixtures()

