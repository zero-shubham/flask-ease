from pydantic.main import ModelMetaclass
import inspect
import re
from uuid import UUID
from typing import Callable
from enum import Enum
import http
from flask_ease.schemas import Form
from flask_ease import status


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


def extract_dependencies(func):
    signature = inspect.signature(func)
    dependencies = {
        k: v.default
        for k, v in signature.parameters.items()
        if isinstance(v.default, Depends) or isinstance(v.default, Security)
    }

    return dependencies


class Depends():
    def __init__(self, dependency: Callable):
        self.dependency = dependency

    def __call__(self):
        dependencies = extract_dependencies(self.dependency)
        kwargs_to_pass = {}
        for k, dep in dependencies.items():
            kwargs_to_pass[k] = dep()
        return self.dependency(**kwargs_to_pass)


class Security():
    def __init__(self, scheme):
        self.scheme = scheme

    def __call__(self):
        token_header = self.scheme()
        if not token_header:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if self.scheme.token_prefix:
            if token_header and self.scheme.token_prefix in token_header:
                token = token_header.replace(self.scheme.token_prefix, "")
                return token
        else:
            return token_header


def get_operation_id(
    path: str,
    endpoint: str,
    method: str
):
    path = path.replace("/", "")
    return f"{endpoint}_{path}__{method}"


def parse_response_models(response_models):
    docs_responses = {}
    docs_definitions = {}
    response_validations = {}
    for model in response_models:
        if type(model.model_schema) == ModelMetaclass:
            schema = model.model_schema.schema()
            status_code = model.status_code
            if "definitions" in schema.keys():
                docs_definitions = {
                    **docs_definitions,
                    **schema["definitions"]
                }
                del schema["definitions"]
            docs_responses = {
                **docs_responses,
                status_code: {
                    "description": model.description,
                    "content": {
                        "application/json": {
                            "schema": schema
                        }
                    }
                }
            }
            response_validations = {
                **response_validations,
                status_code: model.model_schema
            }
    return (docs_responses, docs_definitions, response_validations)


def get_openapi_data_type(_type):
    if _type == int:
        return "integer"
    if _type == float:
        return "number"
    if _type in [str, UUID]:
        return "string"
    if _type in [list, tuple]:
        return "array"
    return "object"


def parse_path_parameter_from_route(route):
    path_param_found = re.search(':[\w_]+', route)
    path_params = []
    while path_param_found:
        start, end = path_param_found.span()
        param = route[start+1:end].strip()
        route = route[end:].strip()
        path_params.append(param)
        path_param_found = re.search(':[\w_]+', route)
    return path_params


def extract_params(route, func):
    path_params = parse_path_parameter_from_route(route)
    doc_details = {
        "params": [],
        "components": {},
        "request_body": {
            "content": {
                "application/json": {},
                "application/x-www-form-urlencoded": {},
                "multipart/form-data": {}
            }
        },
        "definitions": {}
    }
    validations = {
        "params": {},
        "request_body": {}
    }
    signature = inspect.signature(func)

    # * inspecting out the function signature for endpoint method.
    defaults = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    func_args_set = set(func.__annotations__.keys())
    path_params_set = set(path_params)

    if not path_params_set.issubset(func_args_set):
        raise AssertionError(
            f"Path parameters missing from {func.__name__} endpoint method arguments."
        )

    for key, value in func.__annotations__.items():

        if type(value) == type:

            if key in path_params and key in defaults.keys():
                raise AssertionError(
                    f"Path parameters can't have default values. Check {func.__name__} endpoint method."
                )

            doc_details["params"].append({
                "name": key,
                "required": False if key in defaults.keys() else True,
                "in": "path" if key in path_params
                else "query",
                "schema": {
                    "title": key.capitalize(),
                    "type": get_openapi_data_type(value),
                    "default": defaults[key] if key in defaults.keys()
                    else None
                }
            })
            validations["params"] = {
                **validations["params"],
                f"{key}": {
                    "_type": value,
                    "in": "path" if key not in defaults.keys()
                    else "query"
                }
            }
        # * if the parameter is a pydantic ModelMetaClass
        # * it's request body schema
        elif (
            type(value) == ModelMetaclass or
            type(value) == Form
        ):
            if (
                (
                    type(value) == ModelMetaclass and
                    doc_details["request_body"]["content"]["application/json"]
                ) or (
                    type(value) == Form and
                    doc_details["request_body"]["content"][value.media_type]
                )
            ):
                raise Exception(
                    f"""More that one request
                        body found for {func.__name__} endpoint.
                        """
                )
            if type(value) == ModelMetaclass:
                schema = value.schema()
            elif type(value) == Form:
                schema = value.schema.schema()

            if "definitions" in schema.keys():
                doc_details["definitions"] = {
                    **doc_details["definitions"],
                    **schema["definitions"]
                }
                del schema["definitions"]
            title = schema["title"]
            doc_details["components"]["schemas"] = {
                f"{title}": schema
            }

            content_type = "application/json"
            if type(value) == Form:
                content_type = value.media_type

            doc_details["request_body"]["content"][
                content_type] = {
                    "schema": {
                        "$ref": f"#/components/schemas/{title}"
                    }
            }

            validations["request_body"] = {
                f"{key}": {
                    "type": content_type,
                    "schema": (
                        value if type(
                            value) == ModelMetaclass else value.schema
                    )
                }
            }
        else:
            raise TypeError(
                f"""{key} of type {type(value)} is not supported.
                    Use primitive type for declaring query or path parameters.
                    Otherwise pydantic BaseModel for declaring request body."""
            )

    return (doc_details, validations)


def convert_to_openapi_route(route):
    path_params = parse_path_parameter_from_route(route)
    found_count = 0
    path_param_found = re.search('<\w+:[\w_]+>', route)
    while path_param_found:
        start, end = path_param_found.span()
        route = route[:start]+"{"+path_params[found_count]+"}"+route[end:]
        found_count += 1
        path_param_found = re.search('<\w+:[\w_]+>', route)
    return route


def generate_summary(endpoint_method):
    endpoint_method = endpoint_method.replace(".", " -> ")
    endpoint_method = endpoint_method.split("_")
    endpoint_method = [endpoint.capitalize() for endpoint in endpoint_method]
    return " ".join(endpoint_method)


def generate_openapi_paths(endpoints, auth_scheme):
    openapi_paths = {}

    for endpoint, val in endpoints.items():
        path = convert_to_openapi_route(endpoint)
        endpoint_methods = list(val.keys())
        for method in endpoint_methods:
            operation_id = get_operation_id(
                endpoint,
                val[method]["endpoint_method"],
                method
            )
            val[method]["operationId"] = operation_id

            val[method]["summary"] = generate_summary(
                val[method]["endpoint_method"])
            del val[method]["endpoint_method"]

            if val[method]["auth_required"]:
                val[method]["security"] = [
                    {
                        f"{auth_scheme.scheme}": []
                    }
                ]
            del val[method]["auth_required"]

        openapi_paths[path] = val

    return openapi_paths


def generate_auth_scheme(scheme):
    openapi_auth_scheme = {
        f"{scheme.scheme}": {
            "type": scheme.type,
            "flows": {
                f"{scheme.flows}": {
                    "scopes": scheme.scopes,
                    "tokenUrl": scheme.tokenUrl
                }
            }
        }
    }
    return openapi_auth_scheme
