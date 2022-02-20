from .. import exceptions
    
class BaseNextcloudObject:
    
    class DoesNotExist(exceptions.NextcloudDoesNotExist):
        pass
    
    class AlreadyExist(exceptions.NextcloudAlreadyExist):
        pass
    
    class MultipleObjectsReturned(exceptions.NextcloudMultipleObjectsReturned):
        pass

    # TODO DublicateObject exception
    
    def __init_subclass__(cls, manager, pk='name'):
        """
        Set manager class on subclasses, initialize pk
        """
        
        cls.objects = manager(cls)
        cls._pk = pk
    
    def __init__(self, **data):
        self._data = {}
        self._related = {}
        
        self._changes = set()
        self._stored = False
        
        self._init_related()
        
        # set initial attributes
        for k,v in data.items():
            if k in self.synced_relations:
                getattr(self, k)._set_related(v)
            else:
                setattr(self, k, v)
    
    
    def _set_stored(self, data):
        """
        Initialize the instance with the data stored in nextcloud
        """
        
        for k,v in data.items():
            if k in self.synced_relations:
                getattr(self, k)._set_related(v)
            else:
                setattr(self, k, v)
        
        self._changes = set()
        self._stored = True
    
    
    def _init_related(self):
        pass
    
    def __getattr__(self, attr):
        """
        If the attribute is a synced nextcloud attribute, get it from self._data
        """
        
        if attr in self.synced_attributes:
            return self._data.get(attr, None)
    
        if hasattr(super(), attr):
            return getattr(super(), attr)
        
        raise AttributeError(f"{self.__class__.__name__} object has no attribute '{attr}'")
    
    def __setattr__(self, attr, value):
        """
        If the attribute is a synced nextcloud attribute, store it in self._data to keep track of changes
        """
        
        if attr in self.synced_relations:
            
            if hasattr(self, attr):
                raise AttributeError(f"direct assignment of syncronized relations is not possible, use '{attr}.set()' instead")
            
            # setting relation for the first time
            super().__setattr__(attr, value)
            
            return
        
        # track changes for certain atrributes
        if attr in self.synced_attributes:
            if self._data.get(attr) != value:
                self._changes.add(attr)

            self._data[attr] = value
        else:
            super().__setattr__(attr, value)
    
    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.pk == other.pk
    
        return False
    
    def __hash__(self):
        # TODO use self.pk
        return hash((self.__class__.__name__, getattr(self, self._pk)))
    
    @property
    def synced_attributes(self):
        """
        syncronized nextcloud attributes (without relations)
        """
        
        return []
    
    @property
    def synced_relations(self):
        """
        syncronized nextcloud relations (e.g. user-->group)
        """
        
        return []
    
    def save(self):
        """
        apply the changes to nextcloud
        
        - at first the instance needs to be stored if it was not fetched from nextcloud
        - syncronize all relations
        - syncronize every changed attribute 
        """
        
        if not self._stored:
            self._store()
            self._stored = True
        
        for attr in self.synced_relations:
            rel = getattr(self, attr)
            rel._sync()
            
        for attr in self._changes:

            request = self._sync_attribute(attr)
            self.objects.check_request(request)

        
        self._changes = set()
    
    def _delete(self):
        raise NotImplemented()
    
    def delete(self):
        """
        delete the instance from nextcloud
        """
        
        request = self._delete()
        self.objects.check_request(request)
        
        self._stored = False
    
    @property
    def pk(self):
        """
        primary-key of the instance
        """
        
        return getattr(self, self._pk)
    
