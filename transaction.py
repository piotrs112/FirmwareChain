import hashlib
import json
from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from signing import is_signed, numerize_public_key, verify_signature


class Transaction:
    """
    Transaction class containing update data.
    """

    def __init__(self, public_key: RSAPublicKey, data: dict, datetime: datetime = datetime.now()):
        """
        Transaction class constructor
        :param public_key: Author's public key
        :param data: Serializable dict data object
        :param datetime: Transaction Timestamp
        """

        self.public_key = public_key
        self.data = data
        self.signature = None
        self.datetime = datetime

    @property
    def representation(self) -> bytes:
        """
        Returns bytes representation of transaction
        """
        key = self.public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        _data = json.dumps(self.data)
        return b"%s%s%s" % (key, _data.encode(), str(self.datetime.timestamp()).encode())

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
            "data": json.dumps(self.data),
            "signature": signature,
            "datetime": self.datetime.timestamp()
        })

    def __eq__(self, other) -> bool:
        """
        Compare transactions
        :param other: Transaction object to compare to
        """
        if self.data == other.data:
            try:
                if self.public_key.public_numbers() == other.public_key.public_numbers():
                    return True
                else:
                    return False
            except AttributeError:
                return False

        else:
            return False
            # todo porownac podpis i

    def __repr__(self) -> str:
        """
        Representation for debugging purposes
        """
        s = ""
        if is_signed(self):
            s += "Signed: "
            s += str(self.signature)[:5] + " "
        if verify_signature(self):
            s += "Verified"

        return s

    def sha(self):
        """
        Computes sha256 hash of the transaction.
        """

        _bytes = self.representation
        sha = hashlib.sha256(_bytes).hexdigest()
        return int(sha, 16)
