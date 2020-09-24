from dataclasses import asdict
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ..client import AuthenticatedClient, Client
from ..errors import ApiResponseError
from ..models.api_message import APIMessage
from ..models.http_validation_error import HTTPValidationError
from ..models.party_create import PartyCreate
from ..models.party_get import PartyGet
from ..models.party_token_balance import PartyTokenBalance
from ..models.party_token_transfer import PartyTokenTransfer
from ..models.party_token_transfer_receipt import PartyTokenTransferReceipt
from ..models.party_update import PartyUpdate


def get_many_api_parties__get(
    *, client: AuthenticatedClient, offset: Optional[int] = 0, limit: Optional[int] = 20,
) -> Union[List[PartyGet], HTTPValidationError]:

    """  """
    url = "{}/api/parties/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = limit

    response = httpx.get(url=url, headers=headers, params=params,)

    if response.status_code == 200:
        return [PartyGet.from_dict(item) for item in cast(List[Dict[str, Any]], response.json())]
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def create_one_api_parties__post(
    *,
    client: AuthenticatedClient,
    json_body: PartyCreate,
    create_blockchain_account: Optional[bool] = True,
    token_id: Optional[int] = 0,
    initial_amount: Optional[int] = 100000000,
) -> Union[PartyGet, HTTPValidationError]:

    """  """
    url = "{}/api/parties/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if create_blockchain_account is not None:
        params["create_blockchain_account"] = create_blockchain_account
    if token_id is not None:
        params["token_id"] = token_id
    if initial_amount is not None:
        params["initial_amount"] = initial_amount

    json_json_body = json_body.to_dict()

    response = httpx.post(url=url, headers=headers, json=json_json_body, params=params,)

    if response.status_code == 200:
        return PartyGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def get_one_api_parties__uid___get(*, client: AuthenticatedClient, uid: str,) -> Union[PartyGet, HTTPValidationError]:

    """  """
    url = "{}/api/parties/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.get(url=url, headers=headers,)

    if response.status_code == 200:
        return PartyGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def update_one_api_parties__uid___put(
    *, client: AuthenticatedClient, uid: str, json_body: PartyUpdate,
) -> Union[PartyGet, HTTPValidationError]:

    """  """
    url = "{}/api/parties/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    response = httpx.put(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return PartyGet.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def delete_one_api_parties__uid___delete(
    *, client: AuthenticatedClient, uid: str,
) -> Union[APIMessage, HTTPValidationError]:

    """  """
    url = "{}/api/parties/{uid}/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.delete(url=url, headers=headers,)

    if response.status_code == 200:
        return APIMessage.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def get_token_balance_api_parties__uid__token_balance__token_id__get(
    *, client: AuthenticatedClient, uid: str, token_id: int,
) -> Union[PartyTokenBalance, HTTPValidationError]:

    """  """
    url = "{}/api/parties/{uid}/token-balance/{token_id}".format(client.base_url, uid=uid, token_id=token_id)

    headers: Dict[str, Any] = client.get_headers()

    response = httpx.get(url=url, headers=headers,)

    if response.status_code == 200:
        return PartyTokenBalance.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)


def transfer_tokens_api_parties__uid__token_transfer__post(
    *, client: AuthenticatedClient, uid: str, json_body: PartyTokenTransfer,
) -> Union[PartyTokenTransferReceipt, HTTPValidationError]:

    """  """
    url = "{}/api/parties/{uid}/token-transfer/".format(client.base_url, uid=uid)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    response = httpx.post(url=url, headers=headers, json=json_json_body,)

    if response.status_code == 200:
        return PartyTokenTransferReceipt.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 422:
        return HTTPValidationError.from_dict(cast(Dict[str, Any], response.json()))
    else:
        raise ApiResponseError(response=response)
