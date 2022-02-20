
class NextcloudRequestException(Exception):
    
    def __init__(self, request=None, message=None):
        self.request = request
        
        message = message or f"Error {request.status_code}: {request.get_error_message()}"
        super().__init__(message)
        
class NextcloudDoesNotExist(NextcloudRequestException):
    pass


class NextcloudAlreadyExist(NextcloudRequestException):
    pass
 
class NextcloudMultipleObjectsReturned(Exception):
    pass
