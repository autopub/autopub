class AutopubException(Exception):
    message: str


class ReleaseFileNotFound(AutopubException):
    message = "Release file not found"


class ReleaseFileEmpty(AutopubException):
    message = "Release file is empty"


class ReleaseNoteInvalid(AutopubException):
    message = "Release note is invalid"


class MissingReleaseType(AutopubException):
    message: str = "Release note is missing release type"


class InvalidReleaseType(AutopubException):
    def __init__(self, release_type: str):
        self.message = f"Release type {release_type} is invalid"
