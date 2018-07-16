# imports
from flask import Flask

# Creates our application.
app = Flask(__name__)

app.config.from_pyfile('settings/settings.py', silent=True)

app.debug = app.config["DEBUG"]

# DATABASE SETTINGS
host = app.config["DATABASE_HOST"]
port = app.config["DATABASE_PORT"]
user = app.config["DATABASE_USER"]
passwd = app.config["DATABASE_PASSWORD"]
db = app.config["DATABASE_DB"]

from app import views
