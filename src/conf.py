#-*- coding:utf-8 -*-


"""
PGLeon.src.conf
PGLeon Configurator and configuration database access
"""

import os
import sys
from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, TextField, BooleanField

import logging
logger = logging.getLogger(__name__)

name = "PGLeon"
version = "0.1"
title = name
appIcon = ':/pgleon.png'


def localFolder():
    if ('win' in sys.platform) and ('darwin' not in sys.platform):
        import winpaths
        lf = os.path.join(winpaths.get_local_appdata(), name)
    else:
        lf = os.path.join(os.path.expanduser('~'), u'.%s'%name.lower())
    if not os.path.exists(lf):
        os.makedirs(lf)
        logger.info("Configuration directory created under: %s"%lf)
    return lf


dbName = "%s.db"%name.lower()
dbPath = os.path.join(localFolder(), dbName)
# os.remove(dbPath)
try:
    confDB = SqliteDatabase(dbPath)
    logger.info("Configuration database accessible")
except Exception, err:
    logger.error("Configuration database not accessible: %s"%err)
    sys.exit(1)


class DBConfig(Model):
    host = CharField(null=True)
    port = CharField(null=True)
    database = CharField(null=True)
    user = CharField(null=True)
    password = CharField(null=True)
    name = CharField(null=False)

    class Meta:
        database = confDB


class Bookmark(Model):
    """Queries for one database connection"""
    keyword = CharField(null=True)
    name = CharField(null=False)
    isglobal = BooleanField(default=False)
    dbconfig = ForeignKeyField(DBConfig, null=True)
    query = TextField(null=False)

    class Meta:
        database = confDB


DBConfig.create_table(True)
Bookmark.create_table(True)



def fixtures():
    """Create defaults items"""
    qList = [["Tables list", True,
              """--List tables except system ones
SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
AND table_schema NOT IN ('pg_catalog', 'information_schema');"""],
             ["All tables list", True,
              """--List all tables, including system tables
SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE';"""],
             ["Views list", True,
              """--List views except system ones
SELECT table_name
FROM information_schema.views
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
AND table_name !~ '^pg_';"""],
             ["All views list", True,
              """--List all views, including system views
SELECT table_name
FROM information_schema.views;"""]
    ]
    if Bookmark.select().count() == 0:
        for name, isglobal, query in qList:
            sql = Bookmark(name=name, isglobal=isglobal, query=query)
            sql.save()
            logger.info("Fixtures inserted in database")

fixtures()

