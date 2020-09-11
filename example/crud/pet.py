from application import db
from models.Pet import Pet


def find_pet_by_id(_id):
    query = Pet.select().where(
        Pet.columns.id == str(_id)
    )
    pet = db.engine.execute(query).fetchone()
    if pet:
        return dict(pet)


def add_new_pet_to_db(values: dict):
    values["id"] = str(values["id"])
    query = Pet.insert()
    db.session.execute(query, values)
    db.session.commit()
    new_pet = find_pet_by_id(values["id"])
    return new_pet
