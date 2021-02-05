from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey
from pymongo import MongoClient

from signing import directly_numerize_public_key


class ID_bank():
    """
    Used for interacting with MongdoDB id storing.
    :param owner: Owner public key (numerized)
    """

    def __init__(self, owner: str):
        self.owner = owner[:20]
        connection = MongoClient()
        try:
            db = connection.get_database('blockchain')
            # self.db_online = True # online only for now
        except:
            #self.db_online = False
            #print("Connection error")
            raise ConnectionError

        self.collection = db.get_collection(f"id_bank") #_{self.owner}")
        saved_bank = self.collection.find_one({
            'owner': self.owner
        })
        if saved_bank == None:
            self.collection.insert_one({
                'owner': self.owner,
                'bank': dict()
            })

    @property
    def bank(self) -> dict:
        # Update bank
        try:
            bank_obj = self.collection.find_one({'owner': self.owner})['bank']
        except Exception as e:
            raise e

        return dict(bank_obj)
    
    def get(self, pub_key: _RSAPublicKey) -> dict:
        try:
            return self.bank[directly_numerize_public_key(pub_key)]
        except KeyError:
            return None

    def update(self, data: dict):
        """
        Stores data as follows:
        {
            "owner": $pubkey$,
                "bank": {
                        $pubkey$: {
                        "mesh_id": $mesh_id$,
                        "score": $score$
                        }
                 }
        }
        

        """
        bank: dict = self.bank
        print(bank)
        bank.update(data)
        print(bank)
        self.collection.find_one_and_replace({
            'owner': self.owner
        },
            {
                'owner': self.owner,
                'bank': bank
        })

    def remove_bank(self):
        self.collection.delete_one({'owner': self.owner})
        #self.collection.drop(f"id_bank_{self.owner}")

    def modify(self, pub_key: _RSAPublicKey, points=-1) -> bool:
        """
        Adds or subtracts points from peer.
        :param pub_key: Public Key
        :param points: Number of points to add
        """
        if points == 0:
            return

        bank = self.bank
        if data := self.get(pub_key):
            data['score'] = data['score'] + points
            
            if data['score'] < 0:
                data['score'] = 0
            elif data['score'] > 20:
                data['score'] = 20

            self.update({
                directly_numerize_public_key(pub_key): data
            })
