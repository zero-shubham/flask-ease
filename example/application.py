import sys
import pathlib
sys.path.extend([str(pathlib.Path(__file__).parent.parent.absolute())])

from flask_ease import (
    FlaskEaseAPI,
    ResponseModel,
    Depends,
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    Security,
    HTTPException
)
from flask_cors import CORS
import os
import dotenv
from flask import Flask, Blueprint

oauth2_scheme = OAuth2PasswordBearer("/login")

dotenv.load_dotenv()
DATABASE_URI = os.environ["DATABASE_URI"]

my_api = FlaskEaseAPI(auth_scheme=oauth2_scheme)
app = my_api.app
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

