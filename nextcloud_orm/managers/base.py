
class NextcloudManager:

    def __init__(self, model):
        
        self.model = model
        

    def check_request(self, request):
        """
        Check the validity of a nextcloud request and raise a suitable exception otherwise
        """
        
        # TODO improve this (maybe seperate into NextcloudUserManager etc)
        from .. import models
        from .. import exceptions
        
        if not request.is_ok:
            if request.status_code==404:
                raise self.model.DoesNotExist(request)
            
            if request.status_code==102 and request.get_error_message() == 'User already exists':
                raise models.NextcloudUser.AlreadyExist(request)
            
            raise exceptions.NextcloudRequestException(request)
        

    
    def get(self, **kwargs):
        """
        Get exactly one instance by the given kwargs
        """
        
        if self.model._pk in kwargs:
            obj = self.model(**kwargs) # TODO rm kwargs here
            raw = obj._load()
            obj.raw_data = raw
            
            # TODO check all other attributes from kwargs
        
            return obj
    
        objs = self.filter(**kwargs)
        
        if not len(objs):
            raise self.model.DoesNotExist(message='Error: the requested model does not exist')
        
        # TODO len>2 raise ambiguous
        if len(objs)>1:
            raise self.model.NextcloudMultipleObjectsReturned(message='Error: get() returned more than one instance')
        
        return objs[0]
        
    
    def get_or_create(self, defaults={}, **kwargs):
        """
        Get an instance from nextcloud if it exists, or create it with the specified default values otherwise
        """
        
        try:
            obj = self.get(**kwargs)
        except self.model.DoesNotExist:
            data = {**defaults, **kwargs}
            obj = self.model(**data)
            obj.save()
        
        return obj
    
    
    def all(self):
        """
        Query every instance from nextcloud
        """
        
        raise NotImplemented()
    
    def _pre_filter(self, **kwargs):
        """
        Prefiltering that can be overriden to save unnecessary queries
        """
        
        return kwargs, self.all()
    
    def filter(self, **kwargs):
        """
        Query every instance from nextcloud that has the properties specified via kwargs
        """
        
        from . import related
        
        updated_kwargs, objs = self._pre_filter(**kwargs)
        
        filtered = []
        
        for instance in objs:
            valid = True
            
            # TODO seperate method: check_attributes
            for attr, value in updated_kwargs.items():
                
                inst_val = getattr(instance, attr)
                
                if isinstance(inst_val, related.NextcloudRelatedManager):
                    if not inst_val.contains(value):
                        valid = False
                elif inst_val!=value:
                    valid = False
            
            if valid:
                filtered.append(instance)
        
        return filtered
    
