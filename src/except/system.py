class InternalError(Exception):
    """
    Error caused by software internal mechanism. Users should not handle them by themselves, but report the error
    message to developers.
    """
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code
