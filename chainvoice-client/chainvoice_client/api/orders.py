from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ..client import AuthenticatedClient, Client
from ..errors import ApiResponseError
from ..models.api_message import APIMessage
from ..models.http_validation_error import HTTPValidationError
from ..models.order_create import OrderCreate
from ..models.order_get import OrderGet
from ..models.order_update import OrderUpdate


def get_many_api_orders__get(
    *,
    client: AuthenticatedClient,
    offset: Optional[int] = 0,
    limit: Optional[int] = 20,
    seller_uid: Optional[str] = None,
    customer_uid: Optional[str] = None,
) -> Union[List[OrderGet], HTTPValidationError]:

    """  """
    url = "{}/api/orders/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = limit
    if seller_uid is not None:
        params["seller_uid"] = seller_uid
    if customer_uid is not None:
        params["customer_uid"] = customer_uid

    response = httpx.get(url=url, headers=headers, params=params,)

    if response.status_code == 200:
        return [OrderGet.from_dict(item) for item in cast(List[Dict[str, Any]], response.json())]
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def create_one_api_orders__post(
    *, client: AuthenticatedClient, json_body: OrderCreate,
) -> Union[OrderGet, HTTPValidationError]:

    """  """
    url = "{}/api/orders/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    response = httpx.post(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return OrderGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def get_one_api_orders__uid___get(*, client: AuthenticatedClient, uid: str,) -> Union[OrderGet, HTTPValidationError]:

    """  """
    url = "{}/api/orders/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.get(url=url, headers=headers,)

    if response.status_code == 200:
        return OrderGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def update_one_api_orders__uid___put(
    *, client: AuthenticatedClient, uid: str, json_body: OrderUpdate,
) -> Union[OrderGet, HTTPValidationError]:

    """  """
    url = "{}/api/orders/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    response = httpx.put(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return OrderGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def delete_one_api_orders__uid___delete(
    *, client: AuthenticatedClient, uid: str,
) -> Union[APIMessage, HTTPValidationError]:

    """  """
    url = "{}/api/orders/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.delete(url=url, headers=headers,)

    if response.status_code == 200:
        return APIMessage.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)
