from .base import BaseNextcloudObject
from ..managers import NextcloudUserManager, related

class NextcloudUser(BaseNextcloudObject, manager=NextcloudUserManager):
    
    
    ATTRIBUTES = ['email', 'quota', 'phone', 'address', 'website', 'twitter', 'displayname', 'password']
    
    synced_attributes = ATTRIBUTES+['name', 'enabled']
    synced_relations = ['groups', 'subadmin']
    
    
    def __init__(self, name=None, **data):
        if name is None:
            raise ValueError('You need to provide a username')
            
        super().__init__(name=name, **data)
    
    
    def _init_related(self):
        """
        The user is related to a group either as member or as subadmin
        """
        
        from .group import NextcloudGroup
        
        self.groups = related.UserGroupRelation(NextcloudGroup, self)
        self.subadmin = related.UserSubadminRelation(NextcloudGroup, self)
    
    
    def _load(self):
        
        request = self.objects.api.get_user(self.name)
        self.objects.check_request(request)
        
        data = request.data.copy()
        data.pop('id') # this is just the name
        quota = data.pop('quota')
        
        # split up quota dict
        data['quota'] = None if quota['quota']=='none' else quota['quota']
        
        self._set_stored(data)
        
        self.quota_used = quota['used']
        
        return request.data
    
    
    def _store(self):
        
        if self.password:
            request = self.objects.api.add_user(self.name, self.password)

            changes = set(self._data.keys()) - {'name', 'password'}
        elif self.email:
            # not so nice, but not directly accesible through self.api
            requester = nextcloud.api_wrappers.user.User(self.objects.api).requester
            request = requester.post(data=msg)

            changes = set(self._data.keys()) - {'name', 'email'}
        else:
            raise ValueError('To create a nextcloud user you need to either specify a password or an email.')

        self.objects.check_request(request)
        self._changes = changes
        
    
    def _sync_attribute(self, attr):
        
        if attr == 'name':
            raise NotImplemented('User renaming is not supported')
            
        if attr == 'enabled':
            if self.enabled:
                return self.objects.api.enable_user(self.name)
            
            return self.objects.api.disable_user(self.name)
        
        if attr=='quota' and self.quota is None:
            value = 'none'
        else:
            value = getattr(self, attr)
            
        return self.objects.api.edit_user(self.name, attr, value)
        
    def _delete(self):
        return self.objects.api.delete_user(self.name)
    
    def enable(self, value=True):
        """
        Enable an user
        """
        
        self.enabled = value
        
    def disable(self):
        """
        Disable an user
        """
        
        self.enable(False)
        
    def resend_welcome_mail(self):
        """
        Resend the welcome mail to an user
        """
        
        request = self.objects.api.resend_welcome_mail(self.name)
        self.objects.check_request(request)
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"
