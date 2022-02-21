import os
import nextcloud

from . import models
from . import managers

def connect(endpoint=None,
            user=None,
            password=None,
            auth=None,
            session_kwargs=None,
            session=None,
            **kwargs):
    
    # TODO env NEXTCLOUD_URL NEXTCLOUD_USERNAME NEXTCLOUD_PASSWORD
    kwargs['endpoint'] = endpoint or os.environ.get('NEXTCLOUD_HOSTNAME')
    kwargs['user'] = user or os.environ.get('NEXTCLOUD_ADMIN_USER')
    kwargs['password'] = password or os.environ.get('NEXTCLOUD_ADMIN_PASSWORD')
    kwargs['auth'] = auth
    kwargs['session_kwargs'] = session_kwargs
    kwargs['session'] = session
    
    if not session and not all(kwargs[x] for x in ['endpoint', 'user', 'password']):
        raise ValueError("Your connection settings are incomplete. Either specify 'endpoint', 'user' and 'password', or pass a 'session'. "+
                         "If you like to use environment variables, you may set 'NEXTCLOUD_HOSTNAME', 'NEXTCLOUD_ADMIN_USER' and 'NEXTCLOUD_ADMIN_PASSWORD'")
    
    managers.NextcloudManager.api = nextcloud.NextCloud(**kwargs) 
