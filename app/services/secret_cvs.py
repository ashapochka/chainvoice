from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import (SecretClient, KeyVaultSecret)

from ..config import get_settings


class SecretService:
    credential: DefaultAzureCredential
    secret_client: SecretClient

    def __init__(self):
        self.credential = DefaultAzureCredential()

        # noinspection PyTypeChecker
        self.secret_client = SecretClient(
            vault_url=get_settings().key_vault_url,
            credential=self.credential
        )

    def set_secret(self, name, value, **kwargs) -> KeyVaultSecret:
        secret = self.secret_client.set_secret(name, value, **kwargs)
        return secret

    def get_secret(self, name, version=None, **kwargs) -> KeyVaultSecret:
        secret = self.secret_client.get_secret(name, version=version, **kwargs)
        return secret

    def get_secret_value(self, name, version=None, **kwargs) -> str:
        return self.get_secret(name, version=version, **kwargs).value

    def delete_secret(self, name):
        return self.secret_client.begin_delete_secret(name)


secret_service = SecretService()
