from .base import BaseNextcloudObject
from ..managers import NextcloudGroupFolderManager, related

class FolderPermission:
    WRITE = 4 | 2
    DELETE = 8
    SHARE = 16
    
    
    synced_attributes = ['write', 'delete', 'share']
    
    
    def __init__(self, group, folder, code=None, write=True, delete=True, share=True):
        # default code: 31 (all true)
        
        self._data = {}
        self._changes = set()
        
        if code is not None:
            self.write = code & self.WRITE > 0
            self.delete = code & self.DELETE > 0
            self.share = code & self.SHARE > 0
        else:
            self.write = write
            self.delete = delete
            self.share = share

        self._changes = set()
        
        self.group = group
        self.folder = folder
    
        
    def __getattr__(self, attr):
        # copy from BaseNextcloudObject
        
        if attr in self.synced_attributes:
            return self._data.get(attr, None)
    
        if hasattr(super(), attr):
            return getattr(super(), attr)
        
        raise AttributeError(f"{self.__class__.__name__} object has no attribute '{attr}'")
    
    def __setattr__(self, attr, value):
        # copy from BaseNextcloudObject
        
        # track changes for certain atrributes
        if attr in self.synced_attributes:
            if self._data.get(attr) != value:
                self._changes.add(attr)

            self._data[attr] = value
        else:
            super().__setattr__(attr, value)
            
    
    def __repr__(self):
        return f"{self.__class__.__name__}(write={self.write}, delete={self.delete}, share={self.share})"
    
    def __eq__(self, other):
        return all(getattr(self, attr)==getattr(other, attr) for attr in ['write', 'delete', 'share'])
    
    def code(self):
        return self.write*self.WRITE + self.delete*self.DELETE + self.share*self.SHARE + 1
    
    
    def save(self, stored=True):
        
        if not stored or self._changes:
            request = self.folder.objects.api.set_permissions_to_group_folder(self.folder.pk, self.group.pk, self.code())
            
            self.folder.objects.check_request(request)


class NextcloudGroupFolder(BaseNextcloudObject, manager=NextcloudGroupFolderManager, pk='id'):
    
    synced_relations = ['groups']
    synced_attributes = ['mount_point', 'quota']
    
    UNLIMITED_QUOTA = -3
    
    
    def __init__(self, mount_point=None, **kwargs):
        
        for attr in ['quota', 'size', 'id']:
            
            if attr in kwargs:
                value = kwargs[attr]
                kwargs[attr] = int(value) if value is not None else None
        
        super().__init__(mount_point=mount_point, id=kwargs.pop('id', None), **kwargs)
   
    def _init_related(self):
        
        from .group import NextcloudGroup
        
        self.groups = related.FolderGroupRelation(NextcloudGroup, self)
    
    
    def _load(self):
        """
        Load the folder details from nextcloud
        """
        
        request = self.objects.api.get_group_folder(self.id)
        
        # check does not work for non-existant folders 
        self.objects.check_request(request)
        if not request.data:
            raise self.__class__.DoesNotExist(request)
        
        data = request.data.copy()
        data.pop('id')
        data['quota'] = int(data['quota'])
        data['size'] = int(data['size'])
        
        
        self._set_stored(data)
        self._stored = True
        
        return request.data

    def _store(self):
        
        request = self.objects.api.create_group_folder(self.mount_point)
        self.objects.check_request(request)
        self.id = request.data['id']
        
        self._changes = set(self._data.keys())
    
    def _delete(self):
        return self.objects.api.delete_group_folder(self.id)
    
    
    def _sync_attribute(self, attr):
        
        if attr == 'mount_point':
            return self.objects.api.rename_group_folder(self.id, self.mount_point)
        
        # quota needs special treatment
        if attr=='quota':
            if self.quota is None:
                value = self.UNLIMITED_QUOTA
            else:
                value = getattr(self, attr)
        
            return self.objects.api.set_quota_of_group_folder(self.id, value)
        
        raise ValueError('Unknown attribute')
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.mount_point}')"
    
    
    @property
    def pk(self):
        pk = getattr(self, self._pk)
        
        if pk is None:
            return f"auto_{self.mount_point}"
        return pk
