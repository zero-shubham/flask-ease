from flask import Flask
from db import db
from application import (
    app,
    my_api
)
from resources import (
    user,
    auth,
    pet
)


db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


my_api.extend([pet.pets_blp])
my_api.generate()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
