from .base import NextcloudManager
   
class NextcloudAppManager(NextcloudManager):
    
    def _all(self, enabled=None):
        """
        Query all installed apps (either enabled/disabled or both)
        """
        
        if enabled is None:
            request = self.api.get_apps()
        elif enabled is True:
            request = self.api.get_apps(filter='enabled')
        elif enabled is False:
            request = self.api.get_apps(filter='disabled')
            
            self.check_request(request)

            objs = []
            # each app is a key,value pair here
            for id in request.data['apps'].values():
                objs.append(self.get(id))

            return objs
        else:
            raise ValueError("enabled needs to be either True, False or None")
            
        self.check_request(request)
        
        objs = []
        for id in request.data['apps']:
            objs.append(self.get(id))
            
        return objs
    
    def all(self):
        """
        Query all installed apps
        """
        
        return self._all()
    
    def _pre_filter(self, enabled=None, **kwargs):
        """
        Filter the installed apps
        """
        
        return kwargs, self._all(enabled=enabled)
    
    def get(self, id=None, **kwargs):
        """
        Get a specific (installed) app
        """
        
        if id is not None:
            kwargs['id'] = id
        
        return super().get(**kwargs)

