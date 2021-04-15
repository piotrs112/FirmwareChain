def add_one(uuid: str, zones):
    _modify_one_permission(uuid, zones, "add")

def remove_one(uuid: str, zones):
    _modify_one_permission(uuid, zones, "remove")

def add_many_many(uuid: str, zones):
    _modify_one_permission(uuid, zones, "add")

def _modify_one_permission(uuid: str, zones, command: str) -> dict:
    """
    Add permission for one person:
    :param uuid: User UUID
    :param zone: Zone list or str
    """
    return {
        command: [{
            'uuid': uuid,
            'zone': [zones] if type(zones) == str else zones,
        }]
    }

def _modify_permission(uuids: list, zones, command: str) -> dict:
    """
    Add same zone permissions for multiple users
    """
    _dict = {command: []}
    for uuid in uuids:
        _dict[command].append({
            'uuid': uuid,
            'zone': [zones] if type(zones) == str else zones,
        })
    
    return _dict