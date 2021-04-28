from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import (RSAPrivateKey,
                                                           RSAPublicKey,
                                                           RSAPublicNumbers)


def sign(obj, key: RSAPrivateKey):
    """
    Signs block or transaction with given key.
    :param key: Master Private Key
    """

    data = obj.sha().to_bytes(32, 'big')

    obj.signature = key.sign(
        data,
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

    data = obj.sha().to_bytes(32, 'big')

    try:
        obj.public_key.verify(
            obj.signature,
            data,
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

    pub_key = getattr(o, 'public_key')
    if pub_key is not None:
        return directly_numerize_public_key(pub_key)
    else:
        raise AttributeError("Object doesn't have a public key.")


def directly_numerize_public_key(key: RSAPublicKey) -> str:
    """
    Returns given public key in a numeric, human readable format
    """
    n = key.public_numbers().n
    e = key.public_numbers().e
    return f"{n}|{e}"


def denumerize_public_key(key_numeric: str) -> RSAPublicKey:
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
