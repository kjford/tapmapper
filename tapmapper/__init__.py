from flask import Flask

# Creates our application.
app = Flask(__name__)

app.config.from_pyfile('settings/settings.py', silent=True)

app.debug = app.config["DEBUG"]

if not app.debug:
    import logging
    file_handler = logging.FileHandler('/var/log/tapmapper.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

import views
