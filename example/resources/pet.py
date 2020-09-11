from application import (
    my_api,
    Depends,
    HTTPException,
    status
)
from schemas.pet import (
    PetCreationForm,
    PetInResp,
    PetInDB
)
from utils.dependencies import get_current_user
from crud.pet import (
    add_new_pet_to_db
)
from uuid import uuid4


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
