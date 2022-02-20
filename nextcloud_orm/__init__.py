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
    
    managers.NextcloudManager.api = nextcloud.NextCloud(**kwargs) 
