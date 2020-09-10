from flask import (
    Blueprint,
    Flask,
    request,
    render_template_string
)
from typing import (
    List
)
from flask_ease.schemas import ResponseModel
from pydantic.main import ModelMetaclass
from flask_ease.utils import (
    get_operation_id,
    parse_response_model,
    extract_params,
    extract_dependencies,
    generate_openapi_paths,
    generate_auth_scheme,
    HTTPException,
    check_file_validity,
    extract_files_from_request
)
from flask_ease.templates.swagger_ui import html as swagger_html
from flask_ease.templates.redoc_ui import html as redoc_html
import logging
import json
from flask_ease.exceptions import messages


class FlaskEaseAPI():
    def __init__(
        self,
        title: str = "FlaskEase API Docs",
        blueprint_name: str = None,
        open_api_version: str = "3.0.3",
        app_version: str = "0.1.0",
        auth_scheme=None
    ):
        self.blueprint_name = blueprint_name
        if blueprint_name:
            self.app = Blueprint(blueprint_name, __name__)
        else:
            self.app = Flask(__name__)

        self.app_version = app_version
        self.title = title
        self.endpoints = {}
        self.open_api = {
            "openapi": open_api_version
        }
        self.components = {}
        self.definitions = {}
        self.auth_scheme = auth_scheme

    def generate(self):
        if self.blueprint_name:
            logging.error(messages[0])
            return
        self.open_api = {
            **self.open_api,
            "info": {
                "title": self.title,
                "version": self.app_version
            },
            "components": {
                "schemas": self.components
            },
            "definitions": self.definitions,
            "paths": generate_openapi_paths(self.endpoints, self.auth_scheme)
        }
        if self.auth_scheme:
            self.open_api["components"]["securitySchemes"] = \
                generate_auth_scheme(self.auth_scheme)

        @self.app.route("/docs/openapi.json", methods=['GET'])
        def get_openapi():
            return self.open_api

        @self.app.route("/docs", methods=["GET"])
        def get_swagger_ui():
            return render_template_string(
                swagger_html,
                title=self.title
            )

        @self.app.route("/redoc", methods=["GET"])
        def get_redoc_ui():
            return render_template_string(
                redoc_html,
                title=self.title
            )

    def _register(
        self,
        route: str,
        methods: List[str],
        response_model=None,
        tags: List[str] = [],
        auth_required: bool = False,
        responses: dict = {}
    ):
        def decorate_func(func):
            doc_details, validations = extract_params(route, func)

            docs_responses, docs_definitions, response_validations = \
                parse_response_model(response_model, responses)

            dependencies = extract_dependencies(func)

            filtered_req_body = {
                k: v
                for k, v in doc_details["request_body"]["content"].items()
                if v
            }
            endpoint_doc_details = {
                "description": func.__doc__.strip() if func.__doc__ else "",
                "parameters": doc_details["params"],
                "tags": tags,
                "requestBody": {
                    "content": filtered_req_body
                },
                "endpoint_method": func.__name__,
                "responses": docs_responses,
                "auth_required": auth_required
            }

            if route in self.endpoints.keys():
                self.endpoints[route][
                    methods[0].lower()
                ] = endpoint_doc_details
            else:
                self.endpoints[route] = {
                    f"{methods[0].lower()}": endpoint_doc_details
                }

            if (
                "components" in doc_details.keys() and
                "schemas" in doc_details["components"].keys()
            ):
                self.components = {
                    **self.components,
                    **doc_details["components"]["schemas"]
                }

            self.definitions = {
                **self.definitions,
                **docs_definitions,
                **doc_details["definitions"]
            }

            def provide_request(*args, **kwargs):
                kwargs_to_pass = kwargs
                parameter_keys = validations["params"].keys()

                request_body_key = None
                request_form_key = None
                if validations["request_body"]:
                    request_body_key = list(
                        validations["request_body"].keys())[0]
                if validations["request_form"]:
                    request_form_key = list(
                        validations["request_form"].keys())[0]
                try:
                    for p in parameter_keys:
                        parameter_type = validations["params"][p]["_type"]
                        if validations["params"][p]["in"] == "path":
                            val = request.view_args.get(p)
                            if parameter_type != type(val):
                                val = parameter_type(val)

                            kwargs_to_pass[p] = val

                        elif validations["params"][p]["in"] == "query":
                            query_value = request.args.get(p)
                            if query_value:
                                kwargs_to_pass[p] = parameter_type(
                                    query_value
                                )

                    if request_body_key:
                        request_body_schema = validations[
                            "request_body"][request_body_key]["schema"]

                        if (
                            validations["request_body"][request_body_key]["type"]
                                == "application/json"
                        ):
                            kwargs_to_pass[
                                request_body_key
                            ] = request_body_schema(
                                **request.json
                            )
                        elif(
                            validations["request_body"][request_body_key]["type"]
                            == "file"
                        ):
                            kwargs_to_pass[
                                request_body_key
                            ] = check_file_validity(
                                request.data,
                                request.mimetype,
                                request_body_schema
                            )

                    if request_form_key:
                        request_form_schema = validations[
                            "request_form"][request_form_key]["schema"]
                        if (
                            "properties" in
                            validations["request_form"][request_form_key]
                        ):
                            request_form_props = validations[
                                "request_form"][request_form_key]["properties"]

                        form_data = {}
                        if (
                            validations["request_form"][
                                request_form_key]["type"] == "multipart/form-data"
                        ):
                            for k, v in request_form_props.items():
                                if v["type"] == ('string', 'binary'):
                                    form_data[k] = \
                                        extract_files_from_request(
                                        k,
                                        request.files,
                                        v["schema"]
                                    )
                                else:
                                    if k in request.form:
                                        form_data[k] = request.form[k]
                                    else:
                                        form_data[k] = None
                            request_form_schema.schema(**form_data)
                            kwargs_to_pass[
                                request_form_key
                            ] = form_data
                        else:
                            kwargs_to_pass[
                                request_form_key
                            ] = request_form_schema(
                                **request.form
                            )

                    try:
                        # *resolve all the dependencies
                        for k, dep in dependencies.items():
                            kwargs_to_pass[k] = dep()

                        resp = func(**kwargs_to_pass)
                        response = resp
                        response_code = 200
                        if type(resp) == tuple:
                            response, response_code = resp
                        if response_code in response_validations.keys():
                            if type(response) is response_validations[
                                    response_code]:
                                response = response.dict()

                            response_validations[response_code](**response)
                    except Exception as e:
                        logging.exception(e)
                        response = {
                            "detail": "Something went wrong internally."
                        }
                        response_code = 500
                        if type(e) == HTTPException:
                            response = {
                                "detail":   e.detail
                            }
                            response_code = e.status_code
                except Exception as e:
                    logging.exception(e)
                    if type(e) == ValueError:
                        response = {
                            "detail": " ".join(e.args)
                        }
                    else:
                        response = {
                            "detail": json.loads(e.json())
                        }
                    response_code = 422

                return response, response_code

            provide_request.__name__ = func.__name__
            self.app.add_url_rule(
                rule=route,
                endpoint=func.__name__,
                view_func=provide_request,
                methods=methods
            )
        return decorate_func

    def get(
        self,
        route: str,
        response_model=None,
        tags: List[str] = [],
        auth_required: bool = False,
        responses: dict = {}
    ):
        return self._register(
            route,
            ["GET"],
            response_model,
            tags,
            auth_required
        )

    def post(
        self,
        route: str,
        response_model=None,
        tags: List[str] = [],
        auth_required: bool = False,
        responses: dict = {}
    ):
        return self._register(
            route,
            ["POST"],
            response_model,
            tags,
            auth_required
        )

    def put(
        self,
        route: str,
        response_model=None,
        tags: List[str] = [],
        auth_required: bool = False,
        responses: dict = {}
    ):
        return self._register(
            route,
            ["PUT"],
            response_model,
            tags,
            auth_required
        )

    def patch(
        self,
        route: str,
        response_model=None,
        tags: List[str] = [],
        auth_required: bool = False,
        responses: dict = {}
    ):
        return self._register(
            route,
            ["PATCH"],
            response_model,
            tags,
            auth_required
        )

    def delete(
        self,
        route: str,
        response_model=None,
        tags: List[str] = [],
        auth_required: bool = False,
        responses: dict = {}
    ):
        return self._register(
            route,
            ["DELETE"],
            response_model,
            tags,
            auth_required
        )

    def extend(self, blueprints: list):
        for blueprint in blueprints:
            self.app.register_blueprint(
                blueprint.app)
            self.endpoints = {
                **self.endpoints,
                **blueprint.endpoints
            }
            self.components = {
                **self.components,
                **blueprint.components
            }
            self.definitions = {
                **self.definitions,
                **blueprint.definitions
            }
