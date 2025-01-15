from pathlib import Path
from typing import cast

from dulwich.porcelain import checkout_branch, open_repo_closing
from dulwich.repo import Repo
from dulwich.objects import Tag
from poetry.repositories.repository import Repository
from poetry.core.constraints.version import Version
from poetry.core.packages.package import Package
from poetry.core.packages.dependency import Dependency
from poetry.vcs.git import Git
from poetry.packages.direct_origin import DirectOrigin
from poetry.core.version.exceptions import InvalidVersionError

from poetry_semver_git_dependency.core.packages.semver_git_dependency import (
    SemverGitDependency,
)
from poetry_semver_git_dependency.repositories.constants import REPO_NAME


def get_tags(repo: Repo) -> list[Tag]:
    with open_repo_closing(repo) as r:
        tags = r.refs.as_dict(b"refs/tags")
        possibly_tag_objects = [repo.get_object(tag_ref) for tag_ref in tags.values()]
        tag_objects = [tag for tag in possibly_tag_objects if isinstance(tag, Tag)]
        return tag_objects


class SemverGitRepository(Repository):
    """
    Repository for all semver git dependencies

    TOOD: we want to make use of HTTPRepository / CacheRepository in the future for better performance
    """

    def __init__(
        self,
    ) -> None:
        super().__init__(
            name=REPO_NAME,
        )
        self.Git = Git

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
            not isinstance(dependency, SemverGitDependency)
            or dependency.source_url is None
        ):
            raise ValueError("SemverGitRepository can only handle SemverGitDependency")

        repo = self.Git.clone(url=dependency.source_url)
        available_tags = get_tags(repo)

        if not available_tags:
            return []

        # find all matching tags
        matched_tags: list[Tag] = []
        for tag in available_tags:
            try:
                version = Version.parse(tag.name.decode("utf-8"))
            except InvalidVersionError:
                continue

            if dependency.constraint.allows(version):
                matched_tags.append(tag)

        path = Path(repo.path)

        # TODO: add support for subdirectory

        packages = []
        for tag in matched_tags:
            _, commit_id = tag._get_object()
            checkout_branch(repo, commit_id)
            package = DirectOrigin.get_package_from_directory(path)
            package._source_type = "git"
            package._source_url = dependency.source_url
            package._source_reference = tag.name.decode("utf-8")
            packages.append(package)
        return packages
