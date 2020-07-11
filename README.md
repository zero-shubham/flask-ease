# FlaskEase

[Flask](http://flask.pocoo.org/) extension for creating REST APIs and OpenAPI docs with ease, inspired from [FastAPI](https://fastapi.tiangolo.com/).

Checkout example [here](https://github.com/zero-shubham/flask-ease/tree/master/example)

## Documentation

Documentation is coming soon :)

## Try Example

<div class="termy">

```console
$ git clone git@github.com:zero-shubham/flask-ease.git
$ cd flask-ease
$ poetry install
$ source "$( poetry env list --full-path )/bin/activate"
$ python example/main.py
```

</div>

Now go to <a href="http://127.0.0.1:5000/docs" class="external-link" target="_blank">http://127.0.0.1:5000/docs</a> to find SwaggerUI docs for your API.

## Simple Usage

```python
from flask_ease import (
  FlaskEaseAPI,
  ResponseModel,
  Depends
)
from pydantic import BaseModel

my_api = FlaskEaseAPI()
app = my_api.app

class ExampleResp(BaseModel):
    txt: str
    para:str
    cool_txt:str
    query:int

class ExampleReqBody(BaseModel):
    txt: str

def call_me_first():
  return "cool"

@my_api.post(
    route="/<string:some_parameter>",
    response_models=[
        ResponseModel(
          model_schema=ExampleResp,
          status_code=200,
          description="success"
        )
    ],
    tags=["example_route"]
)
def get_example(
    some_parameter:str,
    obj_in: ExampleReqBody,
    query:int=0,
    cool=Depends(call_me_first)
):
    # Similar to FastAPI you get everything as argument
    # to endpoint method
    return ExampleResp(
        txt = obj_in.txt,
        para=some_parameter,
        cool_txt=cool,
        query=query
    ), 200


if __name__ == '__main__':
    my_api.generate()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## _For a complete understanding check the example [here](https://github.com/zero-shubham/flask-ease/tree/master/example)_

__File-uploads are not yet supported via FlaskEase - to be added soon__