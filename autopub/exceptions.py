class AutopubException(Exception):
    pass


class ReleaseFileNotFound(AutopubException):
    pass


class ReleaseFileEmpty(AutopubException):
    pass


class ReleaseNoteInvalid(AutopubException):
    pass


class MissingReleaseType(AutopubException):
    pass

class InvalidReleaseType(AutopubException):
    pass