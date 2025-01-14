from pathlib import Path
from typing import cast

from dulwich.porcelain import tag_list, checkout_branch
from dulwich.objects import Tag
from poetry.repositories.repository import Repository
from poetry.core.constraints.version import Version
from poetry.core.packages.package import Package
from poetry.core.packages.dependency import Dependency
from poetry.vcs.git import Git
from poetry.packages.direct_origin import DirectOrigin


from poetry_semvar_git_dependency.core.constraints.version.parser import (
    is_sem_ver_constraint,
)
from poetry_semvar_git_dependency.core.packages.semvar_git_dependency import (
    SemvarGitDependency,
)
from poetry_semvar_git_dependency.repositories.constants import REPO_NAME


class SemvarGitRepository(Repository):
    """
    Repository for all semvar git dependencies

    TOOD: we want to make use of HTTPRepository / CacheRepository in the future for better performance
    """

    def __init__(
        self,
    ) -> None:
        super().__init__(
            name=REPO_NAME,
        )

    def find_packages(self, dependency: Dependency) -> list[Package]:
        """
        Copied from poetry.repositories.repository.Repository.find_packages, except that this callss _find_packages_from_dep instead of _find_packages
        """
        packages = []
        ignored_pre_release_packages = []

        constraint = dependency.constraint
        allow_prereleases = dependency.allows_prereleases()
        for package in self._find_packages_from_dep(dependency):
            if package.yanked and not isinstance(constraint, Version):
                # PEP 592: yanked files are always ignored, unless they are the only
                # file that matches a version specifier that "pins" to an exact
                # version
                continue
            if (
                package.is_prerelease()
                and not allow_prereleases
                and not package.is_direct_origin()
            ):
                ignored_pre_release_packages.append(package)
                continue

            packages.append(package)

        self._log(
            f"{len(packages)} packages found for {dependency.name} {constraint!s}",
            level="debug",
        )

        if allow_prereleases is False:  # in contrast to None!
            return packages
        return packages or ignored_pre_release_packages

    def _find_packages_from_dep(
        self,
        dependency: Dependency,
    ) -> list[Package]:
        """
        Clone HEAD once, then get tags, then checkout to the commit of matching tags (which is required for parsing dependencies)
        See how poetry handles this: https://github.com/python-poetry/poetry/blob/bd500dd3bdfaec3de6894144c9cedb3a9358be84/src/poetry/packages/direct_origin.py#L26

        See: dulwich documentation for git-related operations: https://www.dulwich.io/docs/tutorial/tag.html
        """
        if (
            not isinstance(dependency, SemvarGitDependency)
            or dependency.source_url is None
        ):
            return []

        repo = Git.clone(url=dependency.source_url)
        available_tag_shas = tag_list(repo)  # this returns SHA1 bytes
        available_tags: list[Tag] = [
            cast(Tag, repo.get_object(tag)) for tag in available_tag_shas
        ]
        sem_ver_tags = [
            tag for tag in available_tags if is_sem_ver_constraint(tag.name)
        ]

        if not sem_ver_tags:
            return []

        # find all matching tags
        matched_tags: list[Tag] = []
        for tag in sem_ver_tags:
            if dependency.constraint.allows(Version.parse(tag.name)):
                matched_tags.append(tag)

        path = Path(repo.path)

        # TODO: add support for subdirectory

        packages = []
        for tag in matched_tags:
            checkout_branch(repo, tag.id)
            package = DirectOrigin.get_package_from_directory(path)
            package._source_type = "git"
            package._source_url = dependency.source_url
            package._source_reference = tag.name
            packages.append(package)
        return packages
