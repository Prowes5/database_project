# -*- conding: utf-8 -*-
import os
from datetime import timedelta

DEBUG = False


SECRET_KEY = os.urandom(24)


SQLALCHEMY_TRACK_MODIFICATIONS = True

#dialet+driver://username:password@host/dbname

PERMANENT_SESSION_LIFETIME = timedelta(days=1)

DIALET = "mysql"
DRIVER = "pymysql"
USERNAME = "root"
PASSWORD = "123456"
HOST = "127.0.0.1"
DATABASE = "database_demo"

SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}/{}?charset=utf8'.format(DIALET,DRIVER,USERNAME,PASSWORD,HOST,DATABASE)
