from poetry.core.packages.dependency import Dependency

from poetry_semver_git_dependency.repositories.constants import REPO_NAME


class SemverGitDependency(Dependency):
    """
    This class should not be instantiated with `create_from_pep_508` (because semver dependency is not pep508 conmpliant);
    Instead, directly instantiate this class
    """

    def __init__(self, name: str, source_url: str, semver_tag: str) -> None:
        source_type = REPO_NAME  # this can't be "git" because if set to `git`, poetry will validate the path and raise error
        super().__init__(
            name=name,
            constraint=semver_tag,
            source_url=source_url,
            source_type=source_type,
        )  # FIXME: for now we assume no extras
        self.source_name = REPO_NAME  # this is used to find the corresponding repository: https://github.com/python-poetry/poetry/blob/bd500dd3bdfaec3de6894144c9cedb3a9358be84/src/poetry/repositories/repository_pool.py#L174

    def is_direct_origin(self) -> bool:
        # by default if `source_type` is "git" it is a direct origin;
        # poetry handles direct origin dependency differently from pypi packages and we can't retrieve multiple versions if so
        # hence, this needs to be explicitly set to False
        # see: https://github.com/python-poetry/poetry/blob/bd500dd3bdfaec3de6894144c9cedb3a9358be84/src/poetry/puzzle/provider.py#L249-L284
        return False
