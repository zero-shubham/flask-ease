from pydantic.main import ModelMetaclass
from dataclasses import (
    asdict
)
import inspect
import re
from uuid import UUID
from typing import (
    Callable,
    List,
    Union
)
from enum import Enum
import http
from flask_ease.schemas import (
    Form,
    File,
    MultipartForm
)
from flask_ease import status
from flask_ease.exceptions import messages


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


def parse_response_model(model, responses):
    docs_responses = {}
    docs_definitions = {}
    response_validations = {}
    if type(model) == ModelMetaclass:
        schema = model.schema()
        status_code = 200
        if "definitions" in schema.keys():
            docs_definitions = {
                **docs_definitions,
                **schema["definitions"]
            }
            del schema["definitions"]
        docs_responses = {
            **docs_responses,
            status_code: {
                "description": "Success",
                "content": {
                    "application/json": {
                        "schema": schema
                    }
                }
            }
        }
        response_validations = {
            **response_validations,
            status_code: model
        }
    for status_code, description in responses.items():
        docs_responses = {
            **docs_responses,
            status_code: {
                "description": description,
                "content": {
                    "application/json": {
                        "schema": schema
                    }
                }
            }
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
    if issubclass(_type, File):
        return ("string", "binary")
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


def get_origins(members):
    origins = list()
    for member in members:
        if member[0] == "__origin__":
            origins.append(member[1])
        if member[0] == "__args__":
            origins.extend(member[1])
    origins.reverse()
    return origins


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
        "request_body": {},
        "request_form": {}
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
            messages[3].format(func.__name__)
        )

    for key, value in func.__annotations__.items():

        if type(value) == type:

            if key in path_params and key in defaults.keys():
                raise AssertionError(
                    messages[2].format(func.__name__)
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
                    f"More that one request body found for {func.__name__} endpoint."
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

            if type(value) == ModelMetaclass:
                validations["request_body"] = {
                    f"{key}": {
                        "type": content_type,
                        "schema": value
                    }
                }
            else:
                validations["request_form"] = {
                    f"{key}": {
                        "type": content_type,
                        "schema": value.schema
                    }
                }
        elif type(value) == File:
            doc_details["request_body"]["content"][value.mime_type] = {
                "schema": {
                    "type": "string",
                    "format": "binary"
                }
            }
            validations["request_body"] = {
                f"{key}": {
                    "type": "file",
                    "schema": asdict(value)
                }
            }
        elif type(value) == MultipartForm:
            value_schema = value.schema.schema()
            schema_annotations = value.schema.__annotations__
            schema_properties = {}
            validation_properties = {}
            for k, v in schema_annotations.items():
                origins = get_origins(inspect.getmembers(v))
                if len(origins) and origins[0] == Union:
                    origins = get_origins(inspect.getmembers(origins[-1]))

                if len(origins):
                    if (
                        len(origins) == 2 and get_openapi_data_type(
                            origins[0]) == "array"
                    ):
                        items_type = get_openapi_data_type(
                            origins[1])
                        validation_properties[k] = {
                            "type": items_type,
                            "schema": origins[-1]
                        }
                        if type(items_type) == tuple:
                            schema_properties[k] = {
                                "type": "array",
                                "items": {
                                        "type": items_type[0],
                                        "format": items_type[1]
                                }
                            }
                        else:
                            schema_properties[k] = {
                                "type": "array",
                                "items": {
                                        "type": items_type
                                }
                            }
            done_properties = schema_properties.keys()
            left_out_props = value_schema["properties"]
            for k, v in left_out_props.items():
                if k not in done_properties:
                    optional_type = get_origins(
                        inspect.getmembers(schema_annotations[k])
                    )
                    item_type = get_openapi_data_type(
                        schema_annotations[k] if not len(
                            optional_type) else optional_type[-1]
                    )

                    validation_properties[k] = {
                        "type": item_type,
                        "schema": schema_annotations[k]
                    }
                    if type(item_type) == tuple:
                        schema_properties[k] = {
                            "type": item_type[0],
                            "format": item_type[1]
                        }
                    else:
                        if item_type == "object":
                            schema_name = v["$ref"].split("/")[-1]
                            doc_details["components"]["schemas"] = {
                                f"{schema_name}": value_schema["definitions"][schema_name]
                            }

                            schema_properties[k] = {
                                "type": item_type,
                                "schema": f"#components/schema/{schema_name}"
                            }
                        else:
                            schema_properties[k] = {
                                "type": item_type
                            }

            doc_details["request_body"]["content"][
                "multipart/form-data"
            ] = {
                "schema": {
                    "type": "object",
                    "properties": schema_properties,
                    "required": value_schema["required"]
                }
            }

            validations["request_form"] = {
                f"{key}": {
                    "type": "multipart/form-data",
                    "properties": validation_properties,
                    "schema": value
                }
            }
        else:
            raise TypeError(
                messages[1].format(key, type(value))
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


def check_file_validity(
    received_file,
    file_content_type,
    schema
):
    if file_content_type != schema["mime_type"]:
        raise ValueError("Invalid file type received.")
        return None
    if (
        (
            schema["min_length"]
            and
            len(
                received_file) < schema["min_length"]
        )
    ):
        raise ValueError("Invalid file size received.")
        return None

    if (
        (
            schema["min_length"]
            and
            len(
                received_file) > schema["max_length"]
        )
    ):
        raise ValueError("Invalid file size received.")
        return None

    return received_file


def extract_files_from_request(_key, files_dict, FileType):
    _files = []
    for element in files_dict.lists():
        if element[0] == _key:
            for _file in element[1]:
                _files.append(
                    FileType(
                        mime_type=element[1][0].mimetype,
                        _data=_file
                    )
                )
    if len(_files) == 1:
        return _files[0]
    return _files
