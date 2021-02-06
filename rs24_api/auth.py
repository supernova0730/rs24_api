import os
import base64

USERNAME = os.getenv('CLIENT_USERNAME')
PASSWORD = os.getenv('CLIENT_PASSWORD')


def get_auth_token(username=USERNAME, password=PASSWORD):
    """Generates authentication token using username and password"""

    return 'Basic ' + base64.b64encode(bytes(f'{username}:{password}'.encode('utf-8'))).decode('utf-8')
