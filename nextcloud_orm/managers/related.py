from .base import NextcloudManager

class NextcloudRelatedManager(NextcloudManager):
    
    
    def __init__(self, model, instance, reversed=False, related_pks=[]):
        super().__init__(model)
        
        # memorize (potentially unsaved) instances
        self._instances = {}
        
        self.instance = instance
        self.reversed = reversed
        self._set_related(related_pks)
        
        
    def _set_related(self, values):
        """
        Initialize the relation-manager with the related values
        """
        
        self.set(values)
        
        self._original = set(self._related) # copy!
    
    def all(self):
        """
        Query every related nextcloud instance
        """
        
        key = self.model._pk
        
        # TODO fix against changes!
        
        return [self.get(**{key:x}) for x in self._related]

    
    def add(self, value):
        """
        Add a relation to an instance
        """
        
        if isinstance(value, self.model):
            self._instances[value] = self.model
            
            pk = value.pk
            self._related.add(pk)
            
        elif isinstance(value, str):
            self._related.add(value)
        else:
            raise ValueError(f'adding instance to {self.__class__.__name__} failed, expected instance of type {self.model} but got {type(value)}')
    
    def remove(self, value):
        """
        Remove the relation to an instance
        """
        
        if isinstance(value, self.model):
            # remove if exists
            self._instances.pop(value, None)
            
            pk = value.pk
            self._related.remove(pk)
            
        elif isinstance(value, str):
            self._related.remove(value)
        else:
            raise ValueError(f'removing instance from {self.__class__.__name__} failed, expected instance of type {self.model} but got {type(value)}')
    
    def contains(self, value):
        """
        Check whether the relations contain value
        """
        
        if isinstance(value, self.model):
            pk = getattr(value, value._pk)
            return pk in self._related
        elif isinstance(value, str):
            return value in self._related
        else:
            raise ValueError(f'checking instance containment in {self.__class__.__name__} failed, expected instance of type {self.model} but got {type(value)}')
    
    def set(self, values):
        """
        Set the relations to the given instances
        """
        
        self._related = set()
        self._instances = {}
        
        for value in set(values):
            self.add(value)
    
    def diff(self):
        """
        Changes that were made in the relations
        """
        
        # returns added entries, removed entries
        return self._related - self._original, self._original - self._related
    
    
    def _sync(self):
        """
        Syncronize the relation changes to nextcloud
        """
        
        # TODO use self.instance.pk
        pk = getattr(self.instance, self.instance._pk)
        
        add, remove = self.diff()
        
        for other in add:
            if self.reversed:
                request = self._sync_add(other, pk)
            else:
                request = self._sync_add(pk, other)
                
            self.check_request(request)
            
            self._original.add(other)
        
        for other in remove:
            if self.reversed:
                request = self._sync_remove(other, pk)
            else:
                request = self._sync_remove(pk, other)
                
            self.check_request(request)
            
            self._original.remove(other)
        
        assert(self._original==self._related)
        
        return add, remove
    
    def _sync_add(self, a, b):
        # add relation between a and b to nextcloud
        
        raise NotImplemented()
    
    def _sync_remove(self, a, b):
        # remove relation between a and b from nextcloud
        
        raise NotImplemented()
    
    def __repr__(self):
        return f"NextcloudRelatedManager({repr(self._related)})"


class UserGroupRelation(NextcloudRelatedManager):
    
    def _sync_add(self, user, group):
        return self.api.add_to_group(user, group)
    
    def _sync_remove(self, user, group):
        return self.api.remove_from_group(user, group)


class UserSubadminRelation(NextcloudRelatedManager):
    
    def _sync_add(self, user, group):
        return self.api.create_subadmin(user, group)
    
    def _sync_remove(self, user, group):
        return self.api.remove_subadmin(user, group)


class FolderGroupRelation(NextcloudRelatedManager):
    
    
    def _set_related(self, values):
        from .groupfolder import FolderPermissionHandler
        
        self._permissions = FolderPermissionHandler(self, values)
        
        super()._set_related(self._permissions._permissions.keys())
    
    
    def add(self, value, **permissions):
        """
        Adding a folder-group relation with permissions
        
        By default the permissions are:
        - write=True
        - delete=True
        - share=True
        """
        
        from ..models.groupfolder import FolderPermission
        
        if not isinstance(value, str):

            if self.reversed:
                p = FolderPermission(self.instance, value, **permissions)

                self._permissions._permissions[value] = p
            else:
                p = FolderPermission(value, self.instance, **permissions)

                self._permissions._permissions[value] = p

        return super().add(value)
    
    
    def _sync(self):
        add, remove = super()._sync()
        
        permissions = [v for k,v in self._permissions._permissions.items() if getattr(k, 'pk', k) in add]
        
        for p in permissions:
            # default permission (all allowed)
            stored = p.code == 31
            p.save(stored=stored)

    
    def _sync_add(self, folder, group):
        return self.api.grant_access_to_group_folder(folder, group)
    
    def _sync_remove(self, folder, group):
        return self.api.revoke_access_to_group_folder(folder, group)
    
    @property
    def permissions(self):
        return self._permissions
