import sqlite3
from flask import Flask, render_template, url_for, request, g, flash, abort
from flask_sqlalchemy import SQLAlchemy
from FDataBase import FDataBase
import os


DATABASE = '/tmp/flslite.db'
DEBUG = True
SECRET_KEY = 'dhis788dsoiah78'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, )))