import logging

MONGO = False

_log = logging.getLogger('blockchain')
_log.setLevel(logging.DEBUG)

if MONGO:
    from mongolog.handlers import MongoHandler
    _log.addHandler(MongoHandler.to(db='bc_log', collection='log'))

log = _log
