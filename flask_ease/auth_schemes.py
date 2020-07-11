from flask import request


class OAuth2PasswordBearer:
    def __init__(self, token_url: str):
        self.scheme = "OAuth2PasswordBearer"
        self.tokenUrl = token_url
        self.scopes = {}
        self.type = "oauth2"
        self.flows = "password"
        self.header = "Authorization"
        self.token_prefix = "Bearer "

    def __call__(self):
        if request.headers.has_key(self.header):
            return request.headers[self.header]
