import base64
import json
import os
from enum import Enum

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


class EntryInfo(Enum):
    URL = 0
    PASSWORD = 1
    USERNAME = 2


kdf = Argon2id(length=32, iterations=1, lanes=4, memory_cost=2 ** 21, salt=os.urandom(16))


class AuthObject:
    def __init__(self, url: str, password: str, username: str):
        self.url = url
        self.password = password
        self.username = username

    def to_json(self):
        """
        Format is "url, password, username"
        :return: type[dict]
        """
        return [self.url, self.password, self.username]

    @staticmethod
    def from_json(json) -> AuthObject:
        return AuthObject(json[EntryInfo.URL.value], json[EntryInfo.PASSWORD.value], json[EntryInfo.USERNAME.value])


def read_vault(vault_str: str) -> list[AuthObject]:
    return [AuthObject.from_json(a) for a in json.loads(vault_str)]


def write_vault(file, vault):
    """
    :param file: file
    :param vault: encrypted
    :return:
    """

    with open(file, 'w') as f:
        f.write(vault)


def encrypt_vault(file, password):
    global kdf

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

    vault = base64.urlsafe_b64encode(vault.encode())

    passkey = password.zfill(32)

    with open(file, "wb") as f:
        key = base64.urlsafe_b64encode(passkey if len(passkey) == 32 else passkey[:-(len(passkey) - 32)])
        fer = Fernet(key)
        token = fer.encrypt(vault)
        f.write(token)


def decrypt_file(file, password):
    with open(file, 'rb') as data:
        data = data.read()

    # Convert the password into a key
    passkey = password.zfill(32)
    passkey = passkey if len(passkey) == 32 else passkey[-32:]
    key = base64.urlsafe_b64encode(passkey.encode())
    fer = Fernet(key)
    vault = fer.decrypt(data)

    try:
        # Return the loaded vault
        return json.loads(base64.b64decode(vault))

    except:
        return None


def vault_init(file, sites: str):
    """
    Init Vault. Encrypts the file with the given password. This password is then turned into the master password.
    However, it is not stored. That would just be bad security.
    :param file:
    :param sites:
    :return:
    """

    # Read the vault
    obj: list[AuthObject] = read_vault(sites)

    with open(file, "w") as fil:
        json.dump([o.to_json() for o in obj], fil)

    # Encrypt the vault
    encrypt_vault(file, input('Enter password: ').encode())


if __name__ == '__main__':
    # Main INIT and READ testing

    vault_init('passwords.json',
               '[["undertale.com", "sanstheskeleton", "snasthesnalakon"]]')
    print(decrypt_file('passwords.json', input("PASSWORD: ")))
