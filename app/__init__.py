from flask import Flask
from config import Config
from py2neo import Graph
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
graph = Graph(host='localhost', http_port=11001, bolt_port=11002)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

from app import routes, models
