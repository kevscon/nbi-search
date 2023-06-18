from flask import Flask
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['JSON_SORT_KEYS'] = False

from app import routes
