from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ..client import AuthenticatedClient, Client
from ..errors import ApiResponseError
from ..models.api_message import APIMessage
from ..models.http_validation_error import HTTPValidationError
from ..models.order_item_create import OrderItemCreate
from ..models.order_item_get import OrderItemGet
from ..models.order_item_update import OrderItemUpdate


def get_many_api_order_items__get(
    *,
    client: AuthenticatedClient,
    offset: Optional[int] = 0,
    limit: Optional[int] = 20,
    order_uid: Optional[str] = None,
) -> Union[List[OrderItemGet], HTTPValidationError]:

    """  """
    url = "{}/api/order-items/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = limit
    if order_uid is not None:
        params["order_uid"] = order_uid

    response = httpx.get(url=url, headers=headers, params=params,)

    if response.status_code == 200:
        return [OrderItemGet.from_dict(item) for item in cast(List[Dict[str, Any]], response.json())]
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def create_one_api_order_items__post(
    *, client: AuthenticatedClient, json_body: OrderItemCreate,
) -> Union[OrderItemGet, HTTPValidationError]:

    """  """
    url = "{}/api/order-items/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    response = httpx.post(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return OrderItemGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def get_one_api_order_items__uid___get(
    *, client: AuthenticatedClient, uid: str,
) -> Union[OrderItemGet, HTTPValidationError]:

    """  """
    url = "{}/api/order-items/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.get(url=url, headers=headers,)

    if response.status_code == 200:
        return OrderItemGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def update_one_api_order_items__uid___put(
    *, client: AuthenticatedClient, uid: str, json_body: OrderItemUpdate,
) -> Union[OrderItemGet, HTTPValidationError]:

    """  """
    url = "{}/api/order-items/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    response = httpx.put(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return OrderItemGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def delete_one_api_order_items__uid___delete(
    *, client: AuthenticatedClient, uid: str,
) -> Union[APIMessage, HTTPValidationError]:

    """  """
    url = "{}/api/order-items/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.delete(url=url, headers=headers,)

    if response.status_code == 200:
        return APIMessage.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)