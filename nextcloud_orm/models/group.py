from .base import BaseNextcloudObject
from ..managers import NextcloudGroupManager, related

# TODO check if groupfolders is installed!!
class NextcloudGroup(BaseNextcloudObject, manager=NextcloudGroupManager):
    
    synced_attributes = ['name']
    
    synced_relations = ['users', 'subadmins', 'folders']
    
    
    def __init__(self, name=None, **data):
        
        if name is None:
            raise ValueError('You need to provide a groupname')
        
        super().__init__(name=name, **data)
    
    def _init_related(self):
        """
        groups have three relations:
        
        - users that belong to the group
        - subadmins, users which manage the group
        - folders that are shared among the group (if the nextcloud extention is installed)
        """
        
        from .user import NextcloudUser
        from .groupfolder import NextcloudGroupFolder
        
        self.users = related.UserGroupRelation(NextcloudUser, self, reversed=True)
        self.subadmins = related.UserSubadminRelation(NextcloudUser, self, reversed=True)
        self.folders = related.FolderGroupRelation(NextcloudGroupFolder, self, reversed=True)
    
    
    def _load(self):
        """
        Load the group details from nextcloud
        
        Subadmins and group-folders are not provided sufficiently and need to be queried seperately
        """
        
        from .groupfolder import NextcloudGroupFolder
        
        request = self.objects.api.get_group(self.name)
        self.objects.check_request(request)
        data = request.data.copy()
        
        request = self.objects.api.get_subadmins(self.name)
        self.objects.check_request(request)
        data['subadmins'] = request.data.copy()
        
        # TODO currently this is a bottleneck --> caching
        data['folders'] = NextcloudGroupFolder.objects.filter(groups=self)
        
        self._set_stored(data)
        
        self._stored = True
        
        return data
    
    def _store(self):
        
        request = self.objects.api.add_group(self.name)
        self.objects.check_request(request)
        
        self._changes = set(self._data.keys()) - {'name'}
    
    
    def _sync_attribute(self, attr):
        
        if attr == 'name':
            raise NotImplemented('Group renaming is not supported')
    
    def _delete(self):
        return self.objects.api.delete_group(self.name)
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

