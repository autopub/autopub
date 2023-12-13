from pydantic import ValidationError


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


class ReleaseTypeMissing(AutopubException):
    message: str = "Release note is missing release type"


class ReleaseTypeInvalid(AutopubException):
    def __init__(self, release_type: str):
        self.message = f"Release type {release_type} is invalid"
        super().__init__()


class NoPackageManagerPluginFound(AutopubException):
    message = "No package manager plugin found"


class ArtifactNotFound(AutopubException):
    message = "Artifact not found, did you run `autopub check`?"


class ArtifactHashMismatch(AutopubException):
    message = "Artifact hash mismatch, did you run `autopub check`?"


class CommandFailed(AutopubException):
    def __init__(self, command: list[str], returncode: int) -> None:
        self.message = (
            f"Command {' '.join(command)} failed with return code {returncode}"
        )
        super().__init__()


class InvalidConfiguration(AutopubException):
    def __init__(self, validation_errors: dict[str, ValidationError]) -> None:
        self.message = "Invalid configuration"
        self.validation_errors = validation_errors
        super().__init__()
