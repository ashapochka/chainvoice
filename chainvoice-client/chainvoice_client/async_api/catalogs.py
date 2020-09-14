from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ..client import AuthenticatedClient, Client
from ..errors import ApiResponseError
from ..models.api_message import APIMessage
from ..models.catalog_create import CatalogCreate
from ..models.catalog_get import CatalogGet
from ..models.catalog_update import CatalogUpdate
from ..models.http_validation_error import HTTPValidationError


async def get_many_api_catalogs__get(
    *,
    client: AuthenticatedClient,
    offset: Optional[int] = 0,
    limit: Optional[int] = 20,
    seller_uid: Optional[str] = None,
) -> Union[List[CatalogGet], HTTPValidationError]:

    """  """
    url = "{}/api/catalogs/".format(client.base_url,)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = limit
    if seller_uid is not None:
        params["seller_uid"] = seller_uid

    async with httpx.AsyncClient() as _client:
        response = await _client.get(url=url, headers=headers, params=params,)

    if response.status_code == 200:
        return [CatalogGet.from_dict(item) for item in cast(List[Dict[str, Any]], response.json())]
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def create_one_api_catalogs__post(
    *, client: AuthenticatedClient, json_body: CatalogCreate,
) -> Union[CatalogGet, HTTPValidationError]:

    """  """
    url = "{}/api/catalogs/".format(client.base_url,)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    async with httpx.AsyncClient() as _client:
        response = await _client.post(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return CatalogGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def get_one_api_catalogs__uid___get(
    *, client: AuthenticatedClient, uid: str,
) -> Union[CatalogGet, HTTPValidationError]:

    """  """
    url = "{}/api/catalogs/{uid}/".format(client.base_url, uid=uid,)

    headers: Dict[str, Any] = client.get_headers()

    async with httpx.AsyncClient() as _client:
        response = await _client.get(url=url, headers=headers,)

    if response.status_code == 200:
        return CatalogGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def update_one_api_catalogs__uid___put(
    *, client: AuthenticatedClient, uid: str, json_body: CatalogUpdate,
) -> Union[CatalogGet, HTTPValidationError]:

    """  """
    url = "{}/api/catalogs/{uid}/".format(client.base_url, uid=uid,)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    async with httpx.AsyncClient() as _client:
        response = await _client.put(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return CatalogGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


async def delete_one_api_catalogs__uid___delete(
    *, client: AuthenticatedClient, uid: str,
) -> Union[APIMessage, HTTPValidationError]:

    """  """
    url = "{}/api/catalogs/{uid}/".format(client.base_url, uid=uid,)

    headers: Dict[str, Any] = client.get_headers()

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(url=url, headers=headers,)

    if response.status_code == 200:
        return APIMessage.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)
