from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ..client import AuthenticatedClient, Client
from ..errors import ApiResponseError
from ..models.body_login_access_token_api_login_access_token_post import BodyLoginAccessTokenApiLoginAccessTokenPost
from ..models.http_validation_error import HTTPValidationError
from ..models.token import Token
from ..models.user_get import UserGet


async def login_access_token_api_login_access_token_post(
    *, client: Client, form_data: BodyLoginAccessTokenApiLoginAccessTokenPost,
) -> Union[Token, HTTPValidationError]:

    """ OAuth2 compatible token login, get an access token for future requests """
    url = "{}/api/login/access-token".format(client.base_url,)

    headers: Dict[str, Any] = client.get_headers()

    async with httpx.AsyncClient() as _client:
        response = await _client.post(url=url, headers=headers, data=asdict(form_data),)

    if response.status_code == 200:
        return Token.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def test_token_api_login_token_test_post(*, client: AuthenticatedClient,) -> UserGet:

    """ Test access token """
    url = "{}/api/login/token-test".format(client.base_url,)

    headers: Dict[str, Any] = client.get_headers()

    async with httpx.AsyncClient() as _client:
        response = await _client.post(url=url, headers=headers,)

    if response.status_code == 200:
        return UserGet.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)
