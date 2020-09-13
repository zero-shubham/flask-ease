from flask_ease import (
    FlaskEaseAPI,
    ResponseModel,
    Depends,
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    Security,
    HTTPException,
    MultipartForm,
    File,
    status,
    Form
)
from flask_cors import CORS
import os
import dotenv
from db import db
import sys
import pathlib
sys.path.extend([str(pathlib.Path(__file__).parent.parent.absolute())])


oauth2_scheme = OAuth2PasswordBearer("/login")

dotenv.load_dotenv()
DATABASE_URI = os.environ["DATABASE_URI"]

my_api = FlaskEaseAPI(
    auth_scheme=oauth2_scheme,
    title="Test FlaskEase"
)


app = my_api.app
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
