from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey,
                                                      _RSAPublicKey)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

def sign(obj, key: _RSAPrivateKey):
        """
        Signs transaction with given key.
        :param key: Master Private Key
        """

        obj.signature = key.sign(
            obj.representation,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )


def is_signed(obj):
    """
    Returns True if transaction is signed
    """
    try:
        return obj.signature is not None
    except:
        return False

def verify_signature(obj) -> bool:
        """
        Verifies signed object using a public key.
        """

        try:
            obj.public_key.verify(
                obj.signature,
                obj.representation,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except (InvalidSignature, AttributeError):
            return False
        return True

def numerize_public_key(o: object) -> str:
        """
        Returns public key of an object in a numeric, human readable format
        """
        n = o.public_key.public_numbers().n
        e = o.public_key.public_numbers().e
        return f"{n}|{e}"

def directly_numerize_public_key(key: _RSAPublicKey) -> str:
        n = key.public_numbers().n
        e = key.public_numbers().e
        return f"{n}|{e}"

def denumerize_public_key(key_numeric: str) -> _RSAPublicKey:
    """
    Returns public key from a numeric format
    """
    n, e = key_numeric.split('|')
    return RSAPublicNumbers(int(e), int(n)).public_key()

def is_author_trusted(self):
    """
    Chcecks if author's public key is on the trusted list
    """
    credentials = self.numerize_public_key()

    with open("trusted_keys.json", "r") as file:
        if credentials in file.read().splitlines():
            return True
        else:
            return False