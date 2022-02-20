from .base import NextcloudManager

class NextcloudGroupManager(NextcloudManager):
    
    def all(self, search=None):
        """
        Get all nextcloud groups
        """
        
        request = self.api.get_groups(search=search)
        self.check_request(request)
        
        objs = []
        for name in request.data['groups']:
            objs.append(self.get(name))
            
        return objs
    
    
    def get(self, name=None, **kwargs):
        """
        Get a specific nextcloud group
        """
        
        return super().get(name=name, **kwargs)
