from pymongo import MongoClient

from logger import log, MONGO

def test_logging():
    if MONGO:
        client = MongoClient()
        col = client.get_database('bc_log').get_collection('log')

        log.debug('test')

        assert col.find_one({'message': 'test'})

        # Cleanup
        col.find_one_and_delete({'message': 'test'})