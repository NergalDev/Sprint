import json
import requests


URL_PREFIX = 'http://localhost:8089/'


def test_app():
    data = {
            'title': 'Dyatlov',
            'title_prefix': {
                'value': 'per.'
            },
            'alt_titles': [
                'Schmyatlov'
            ],
            'person': {
                'email': 'john_doe_1969@example.com',
                'username': 'johndoe1969',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+19991234567'
            },
            'geodata': {
                'data': {
                    'coordinates': [
                        '1.33',
                        '-2.66'
                    ],
                    'type': 'Point'
                },
                'altitude': 2789
            },
            'photos': [
                {
                    'title': 'Overlook'
                }
            ]
        }

    response = requests.post(URL_PREFIX + 'submitData/',
                             data={'data': json.dumps(data)},
                             files=[('photo_files', b'')])

    assert response.status_code == 200

    decoded_response = json.loads(response.content.decode())

    assert decoded_response['message'] == 'OK'

    _id = decoded_response['_id']

    response = requests.get(URL_PREFIX + 'submitData/',
                            params={'user__email': 'john_doe_1969@example.com'})

    assert response.status_code == 200
    
    1
