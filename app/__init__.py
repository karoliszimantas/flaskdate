from flask import Flask

app = Flask(__name__, template_folder='static\html')

from app import routes


