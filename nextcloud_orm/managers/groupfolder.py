from .base import NextcloudManager

class FolderPermissionHandler:
    
    def __init__(self, relation, values):
        
        from ..models.groupfolder import FolderPermission
        
        
        if relation.reversed:
            pk = relation.instance.name
            
            # Folder-->Group relation
            instances = {
                x:FolderPermission(relation.instance, x, code=x.raw_data['groups'].get(pk))
                for x in values if x.raw_data['groups'].get(pk)
            }
        else:
            if values:
                instances = {
                    g:FolderPermission(g, relation.instance, code=code)
                    for g,code in values.items()
                }
            else:
                instances = {}
        
        self.relation = relation
        self._permissions = instances
    
    
    def get(self, **kwargs):
        element = self.relation.get(**kwargs)
        
        if self.relation.reversed:
            return self._permissions[element]
        
        return self._permissions[element.pk]
    
    def all(self):
        objs = self.relation.all()
        
        if self.relation.reversed:
            return [self._permissions[x] for x in objs]
        
        return [self._permissions[x.pk] for x in objs]
    
    
    # TODO filter

   
class NextcloudGroupFolderManager(NextcloudManager):
    
    def all(self):
        """
        Get all group folders
        """
        
        request = self.api.get_group_folders()    
        self.check_request(request)
        
        
        objs = []
        for id, values in request.data.items():
            objs.append(self.get(id))
            # faster but incomplete data
            #objs.append(NextcloudGroupFolder(id=id, **values))
            
        return objs
    
    # TODO use global method with pk instead
    def get(self, id=None, **kwargs):
        """
        Get a specific group folder
        """
        
        if id is not None:
            kwargs['id'] = id
            
        return super().get(**kwargs)

