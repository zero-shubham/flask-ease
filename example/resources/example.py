from application import (
    FlaskEaseAPI,
    ResponseModel,
    oauth2_scheme,
    Depends
)
from pydantic import (
    BaseModel
)
from utils.dependencies import (
    get_current_user
)


class ExampleResp(BaseModel):
    txt: str


example_blueprint = FlaskEaseAPI(
    blueprint_name="example_blueprint", auth_scheme=oauth2_scheme)


@example_blueprint.get(
    route="/",
    response_models=[
        ResponseModel(
          model_schema=ExampleResp,
          status_code=200,
          description="success"
        )
    ],
    tags=["example_blueprint"],
    auth_required=True
)
def get_example(
    current_user=Depends(get_current_user)
):
    return {
        "txt": "example"
    }, 200
