from enum import Enum


class PaginationTypes(Enum):
    PAGE = "page"
    OFFSET = "offset"
    CURSOR = "cursor"


class AuthenticationTypes(Enum):
    API_KEY_HEADER = "api_key_header"
    BEARER_TOKEN_HEADER = "bearer_token_header"
    AUTHENTICATION_HEADER = "authentication"
