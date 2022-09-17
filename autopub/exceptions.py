class AutopubException(Exception):
    message: str

    def __init__(self) -> None:
        super().__init__(self.message)


class ReleaseFileNotFound(AutopubException):
    message = "Release file not found"


class ReleaseFileEmpty(AutopubException):
    message = "Release file is empty"


class ReleaseNotesEmpty(AutopubException):
    message = "Release notes are empty"


class MissingReleaseType(AutopubException):
    message: str = "Release note is missing release type"


class InvalidReleaseType(AutopubException):
    def __init__(self, release_type: str):
        self.message = f"Release type {release_type} is invalid"
        super().__init__()


class NoPackageManagerPluginFound(AutopubException):
    message = "No package manager plugin found"
