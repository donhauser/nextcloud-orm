from .base import NextcloudManager

class NextcloudUserManager(NextcloudManager):
    
    def all(self, search=None):
        """
        Query all nextcloud users
        """
        
        request = self.api.get_users(search=search)
        self.check_request(request)
        
        users = []
        for name in request.data['users']:
            
            users.append(self.get(name))
            
        return users
    
    
    def get(self, name=None, **kwargs):
        """
        Get a specific nextcloud user
        """
        
        return super().get(name=name, **kwargs)
