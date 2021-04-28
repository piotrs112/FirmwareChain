def add(data: list, access_list: dict):
    _al = access_list
    for entry in data:
        if entry['uuid'] not in set(_al.keys()):
            _al[entry['uuid']] = []

        _list = _al[entry['uuid']]
        for zone in entry['zone']:
            _list.append(zone)

        _al[entry['uuid']] = _list

    return _al


def remove(data: list, access_list: dict):
    _al = access_list

    for entry in data:
        if entry['uuid'] not in set(_al.keys()):
            _al[entry['uuid']] = []

        _al[entry['uuid']] = [
            a for a in _al[entry['uuid']] if a not in entry['zone']]

    # cleanup
    cp_al = _al.copy()
    for uuid in _al:
        if _al[uuid] == []:
            del cp_al[uuid]

    return cp_al


def build_access_list(data_list: list, access_list: dict):
    for data in data_list:
        if data.get("add"):
            access_list.update(add(data['add'], access_list))
        if data.get("remove"):
            access_list = remove(data['remove'], access_list)
    return access_list
