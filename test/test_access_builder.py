from access_builder import add,remove,build_access_list

def test_add():
    data = [{
        'uuid': 324234,
        'zone': ["door1"]
        },
        {
        'uuid': 767857,
        'zone': ["door1","door2"]
        }
        ]
    assert add(data, {}) == {324234: ["door1"], 767857: ["door1","door2"]}

def test_remove():
    data = [{
        'uuid': 324234,
        'zone': ["door1"]
        },
        {
        'uuid': 767857,
        'zone': ["door2"]
        }
        ]
    access_list = {324234: ["door1"], 767857: ["door1","door2"]}

    assert remove(data, access_list) == {767857: ["door1"]}

def test_build():
    data = [{
        "add": [{
            'uuid': 324234,
            'zone': ["door1"]
            },
            {
            'uuid': 767857,
            'zone': ["door1","door2"]
            }
            ],
        "remove": [{
            'uuid': 324234,
            'zone': ["door1"]
            },
            {
            'uuid': 767857,
            'zone': ["door2"]
            }
            ],
    }]

    assert build_access_list(data, {}) == {767857: ["door1"]}

