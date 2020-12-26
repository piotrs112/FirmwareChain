import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey,
                                                      _RSAPublicKey)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from signing import *


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
        self.signature = None

    @property
    def representation(self) -> bytes:
        """
        Returns bytes representation of transaction
        """
        key = self.public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        return b"%s%s%s%s" % (key, self.version.encode(), self.file_hash.encode(), self.filename.encode())

    def toJSON(self):
        """
        Serialize transaction to JSON format
        """
        try:
            signature = self.signature.hex()
        except AttributeError:
            signature = None
        return json.dumps({
            "public_key": numerize_public_key(self),
            "version": self.version,
            "file_hash": self.file_hash,
            "filename": self.filename,
            "signature": signature
        })

    def __eq__(self, other):
        """
        Compare transactions
        :param other: Transaction object to compare to
        """
        if self.filename == other.filename and self.version == other.version and self.file_hash == other.file_hash:
            return True
        else:
            return False

    def __repr__(self):
        """
        Representation for debuggin purposes
        """
        s = ""
        if is_signed(self):
            s += "Signed: "
            s += str(self.signature) + " "
        if verify_signature(self):
            s += "Verified"

        return s
