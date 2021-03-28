from pymongo import MongoClient

from logger import log

def test_logging():
    client = MongoClient()
    col = client.get_database('bc_log').get_collection('log')

    log.debug('test')

    assert col.find_one({'message': 'test'})

    # Cleanup
    col.find_one_and_delete({'message': 'test'})