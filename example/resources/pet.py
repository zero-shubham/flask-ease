from application import (
    my_api,
    Depends,
    HTTPException,
    status,
    File
)
from schemas.pet import (
    PetCreationForm,
    PetInResp,
    PetInDB,
    PetsInResp
)
from utils.dependencies import get_current_user
from crud.pet import (
    add_new_pet_to_db,
    find_pet_by_id,
    get_all_pets_count_in_db,
    get_all_pets_in_db
)
from uuid import uuid4, UUID
from flask import send_from_directory


@my_api.post(
    route="/pets",
    response_model=PetInResp,
    tags=["pets"],
    auth_required=True
)
def create_new_pet(
    obj_in: PetCreationForm,
    current_user=Depends(get_current_user)
):
    """
    Add a new pet to DB
    """

    if obj_in.owner != current_user["id"]:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not authorised for this operation."
        )

    new_pet = add_new_pet_to_db(PetInDB(
        id=uuid4(),
        **obj_in.dict()
    ).dict())
    return new_pet


@my_api.get(
    route="/pets/<uuid:id>",
    response_model=PetInResp,
    tags=["pets"],
    auth_required=True
)
def get_pet_by_id(
    id: UUID
):
    """
    Get pet by id
    """
    pet = find_pet_by_id(id)
    return pet


@my_api.get(
    route="/pets",
    response_model=PetsInResp,
    tags=["pets"],
    auth_required=True
)
def get_all_pets(
    offset: int = 0,
    limit: int = 10,
    current_user=Depends(get_current_user)
):
    """
    Get all pets in db
    """
    pets = get_all_pets_in_db(
        offset,
        limit
    )
    count = get_all_pets_count_in_db()
    return PetsInResp(
        pets=pets,
        total_count=count
    )


@my_api.post(
    route="/pets/<uuid:id>/photo",
    tags=["pets"],
    auth_required=True,
    responses={
        '204': 'File accepted and saved.'
    }
)
def add_pet_photo(
    id: UUID,
    photo: File("image/png"),
    current_user=Depends(get_current_user)
):
    """
    Add pet photo.
    """
    with open(f"{id}.png", "wb") as photoFile:
        photoFile.write(photo)
    return "True", 204
