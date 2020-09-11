from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ..client import AuthenticatedClient, Client
from ..errors import ApiResponseError
from ..models.api_message import APIMessage
from ..models.http_validation_error import HTTPValidationError
from ..models.user_create import UserCreate
from ..models.user_get import UserGet
from ..models.user_update import UserUpdate


async def get_many_api_users__get(
    *, client: AuthenticatedClient, offset: Optional[int] = 0, limit: Optional[int] = 20,
) -> Union[List[UserGet], HTTPValidationError]:

    """  """
    url = "{}/api/users/".format(client.base_url,)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = limit

    async with httpx.AsyncClient() as _client:
        response = await _client.get(url=url, headers=headers, params=params,)

    if response.status_code == 200:
        return [UserGet.from_dict(item) for item in cast(List[Dict[str, Any]], response.json())]
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def create_one_api_users__post(
    *, client: AuthenticatedClient, json_body: UserCreate,
) -> Union[UserGet, HTTPValidationError]:

    """  """
    url = "{}/api/users/".format(client.base_url,)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    async with httpx.AsyncClient() as _client:
        response = await _client.post(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return UserGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def get_one_api_users__uid___get(
    *, client: AuthenticatedClient, uid: str,
) -> Union[UserGet, HTTPValidationError]:

    """  """
    url = "{}/api/users/{uid}/".format(client.base_url, uid=uid,)

    headers: Dict[str, Any] = client.get_headers()

    async with httpx.AsyncClient() as _client:
        response = await _client.get(url=url, headers=headers,)

    if response.status_code == 200:
        return UserGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def update_one_api_users__uid___put(
    *, client: AuthenticatedClient, uid: str, json_body: UserUpdate,
) -> Union[UserGet, HTTPValidationError]:

    """  """
    url = "{}/api/users/{uid}/".format(client.base_url, uid=uid,)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    async with httpx.AsyncClient() as _client:
        response = await _client.put(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return UserGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def delete_one_api_users__uid___delete(
    *, client: AuthenticatedClient, uid: str,
) -> Union[APIMessage, HTTPValidationError]:

    """  """
    url = "{}/api/users/{uid}/".format(client.base_url, uid=uid,)

    headers: Dict[str, Any] = client.get_headers()

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(url=url, headers=headers,)

    if response.status_code == 200:
        return APIMessage.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)
