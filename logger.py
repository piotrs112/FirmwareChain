import logging

from mongolog.handlers import MongoHandler

_log = logging.getLogger('blochain')
_log.setLevel(logging.DEBUG)
_log.addHandler(MongoHandler.to(db='bc_log', collection='log'))

log = _log