import json
import base64


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
        return AuthObject(json["url"], json["pass"], json["name"])


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
    # check if it's json'
    # if it is, then encript it
    #     save the encripted content to the file
    # if it's not ' do nothing
    with open(file, "r") as f:
        vault = f.read()

    try:
        json.loads(vault)

    except json.decoder.JSONDecodeError:
        return

    with open(file, "w") as f:
        f.write(base64.b64encode(vault.encode()))

vault = []
# what do we do with the functions?
