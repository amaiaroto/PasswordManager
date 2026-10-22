import json
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from enum import Enum

class EntryInfo(Enum):
    URL = 0
    PASSWORD = 1
    USERNAME = 2

def decrypt_file(name: str):
    with open(name, 'rb') as data:
        data = data.read()

    return data

if __name__ == '__main__':
    password = json.loads(decrypt_file('passwords'))
    kdf = Argon2id(length=32, iterations=1, lanes=4, memory_cost=2 ** 21, salt=os.urandom(16))
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(password)


class AuthObject:
    def __init__(self, url: str, password: str, username: str):
        self.url = url
        self.password = password
        self.username = username

    def to_json(self) -> dict:
        """
        Format is "url, password, username"
        :return: type[dict]
        """
        return {"url": self.url, "pass": self.password, "name": self.username}

    @staticmethod
    def from_json(json) -> AuthObject:
        return AuthObject(json[EntryInfo.URL.value], json[EntryInfo.PASSWORD.value], json[EntryInfo.USERNAME.value])


def read_vault(file) -> list[AuthObject]:
    with open(file) as f:
        return [AuthObject.from_json(a) for a in json.load(f)]

def write_vault(file, vault):
    """
    :param file: file
    :param vault: encrypted
    :return:
    """

    with open(file, 'w') as f:
        f.write(vault)

def encprypt_vault(file):
    # open file in reading mode
    # read entire ContentD
    # check if it's json
    # if it is, then encript it
    #     save the encripted content to the file
    # if it's not, do nothing
    with open(file, "r") as f:
        vault = f.read()

    try:
        json.loads(vault)

    except json.decoder.JSONDecodeError:
        return

    with open(file, "w") as f:
        f.write(base64.b64encode(vault.encode()))

vault = read_vault('passwords.json')
# what do we do with the functions?
