import pytest

from vault_cli import client, exceptions


class TestVaultClient(client.VaultClientBase):
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.db = {}
        self.forbidden_list_paths = set()
        self.forbidden_get_paths = set()

    def get_secret(self, path):
        if path in self.forbidden_get_paths:
            raise exceptions.VaultForbidden()
        try:
            return self.db[path]
        except KeyError:
            raise exceptions.VaultSecretNotFound()

    def list_secrets(self, path):
        if path in self.forbidden_list_paths:
            raise exceptions.VaultForbidden()
        # Just reproducing in memory the behaviour of the real list_secrets
        # This is complicated enough to have its unit test, below (test_fake_client)
        paths = [key for key in self.db if key.startswith(path)]
        result = []
        for element in paths:
            element = element[len(path) + 1 if path else 0 :].split("/", 1)
            if len(element) == 1:
                result.append(element[0])
            else:
                result.append(f"{element[0]}/")

        return sorted(set(result) - {""})

    def _set_secret(self, path, value):
        self.db[path] = value

    def delete_secret(self, path):
        self.db.pop(path, None)


@pytest.fixture
def vault(mocker):
    backend = TestVaultClient()
    mocker.patch(
        "vault_cli.client.get_client_class", return_value=lambda **kwargs: backend
    )
    yield backend
