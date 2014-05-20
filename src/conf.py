#-*- coding:utf-8 -*-

__author__ = 'lionel'

"""
PGLeon.src.conf
Gestion de la partie configuration de pgleon.
"""

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, BooleanField

#TODO : mettre la base dans le répertoire personnel de l'utilisateur
conf_db = SqliteDatabase('pgleon.db')


class Connection(Model):
    host = CharField()
    port = CharField()
    database = CharField()
    user = CharField()
    password = CharField()
    name = CharField()

    class Meta:
        database = conf_db
        # indexes = (
        #     # Index unique
        #     (('host', 'port', 'database', 'user'), True),
        # )


class Query(Model):
    connection = ForeignKeyField(Connection, related_name='queries')
    subsection = CharField()
    query = CharField()
    internal = BooleanField(default=False)  # Requetes internes à pgleon, ne pas effacer ni afficher dans l'ui
    deletable = BooleanField(
        default=True)  # Requetes pouvant être effacées. Les requetes globales et internes seront à False

    class Meta:
        database = conf_db


Connection.create_table(True)
Query.create_table(True)

