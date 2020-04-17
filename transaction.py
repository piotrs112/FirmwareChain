import json

from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey,
                                                      _RSAPublicKey)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


class Transaction:
    """
    Transaction class containing update data.
    """

    def __init__(self, public_key: _RSAPublicKey, version: str, file_hash: str, filename: str):
        """
        Transaction class constructor
        :param public_key: Author's public key
        :param version: Software update version
        :param file_hash: SHA256 hash of update file
        :param filename: Name of update file
        """

        self.public_key = public_key
        self.version = version
        self.file_hash = file_hash
        self.filename = filename

    def sign(self, key: _RSAPrivateKey):
        """
        Signs transaction with given key.
        :param key: Master Private Key
        """

        self.signature = key.sign(
            self.representation,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(self) -> bool:
        """
        Verifies signed transaction using a public key.
        """

        try:
            self.public_key.verify(
                self.signature,
                self.representation,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except InvalidSignature:
            return False
        return True

    @property
    def representation(self):
        """
        Returns string representation of transaction
        """
        key = self.public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        return b"%s%s%s%s" % (key, self.version.encode(), self.file_hash.encode(), self.filename.encode())

    def is_author_trusted(self):
        """
        Chcecks if author's public key is on the trusted list
        """
        n = self.public_key.public_numbers().n
        e = self.public_key.public_numbers().e
        credentials = f"{n}|{e}"

        with open("trusted_keys.json", "r") as file:
            if credentials in file.read().splitlines():
                return True
            else:
                return False
