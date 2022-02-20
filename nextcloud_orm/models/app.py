from .base import BaseNextcloudObject
from ..managers import NextcloudAppManager

class NextcloudApp(BaseNextcloudObject, manager=NextcloudAppManager, pk='id'):
    
    def _load(self):
        
        request = self.objects.api.get_app(self.id)
        self.objects.check_request(request)
        data = request.data.copy()
        
        self._set_stored(data)
        self._stored = True
        
        return data
    
    
    def enable(self, enabled=True):
        """
        Enable the app
        """
        
        if enabled==True:
            request = self.objects.api.enable_app(self.id)
        else:
            request = self.objects.api.disable_app(self.id)
        
    def disable(self):
        """
        Disable the app
        """
        
        self.enable(False)
        
        
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}')"
