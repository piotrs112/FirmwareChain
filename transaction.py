from cryptography.hazmat.backends.openssl.rsa import _RSAPrivateKey, _RSAPublicKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


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

        return self.public_key.verify(
            self.signature,
            self.representation,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    @property
    def representation(self):
        """
        Returns string representation of transaction
        """

        return f"{self.public_key}{self.version}{self.file_hash}{self.filename}"
