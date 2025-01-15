from unittest.mock import Mock

import pytest
from dulwich.repo import Repo
from poetry.core.packages.package import Package
from poetry.core.packages.dependency import Dependency

from poetry_semver_git_dependency.core.packages.semver_git_dependency import (
    SemverGitDependency,
)
from poetry_semver_git_dependency.repositories.semver_git_repository import (
    SemverGitRepository,
)
from tests.mock_constants import MOCK_GIT_SOURCE_URL, MOCK_PROJECT_NAME

GIT_1_0_1_PACKAGE = Package(
    MOCK_PROJECT_NAME,
    "1.0.0",
    source_type="git",
    source_url=MOCK_GIT_SOURCE_URL,
    source_reference="1.0.0",
)
GIT_2_0_1_PACKAGE = Package(
    MOCK_PROJECT_NAME,
    "2.0.1",
    source_type="git",
    source_url=MOCK_GIT_SOURCE_URL,
    source_reference="2.0.1",
)
GIT_2_1_1_PACKAGE = Package(
    MOCK_PROJECT_NAME,
    "2.1.1",
    source_type="git",
    source_url=MOCK_GIT_SOURCE_URL,
    source_reference="2.1.1",
)


@pytest.mark.parametrize(
    ("semver_git_dep", "expected_packages"),
    [
        (
            SemverGitDependency(MOCK_PROJECT_NAME, MOCK_GIT_SOURCE_URL, ">=1.0"),
            [
                GIT_1_0_1_PACKAGE,
                GIT_2_0_1_PACKAGE,
                GIT_2_1_1_PACKAGE
            ],
        ),
    ],
)
def test___find_packages_from_dep(
    mock_git_repo: Repo,
    semver_git_dep: SemverGitDependency,
    expected_packages: list[Package],
) -> None:
    mock_Git = Mock()
    mock_Git.clone = Mock(return_value=mock_git_repo)
    repo = SemverGitRepository()
    repo.Git = mock_Git
    assert set(repo._find_packages_from_dep(semver_git_dep)) == set(expected_packages)


def test_fail___find_packages_from_dep() -> None:
    repo = SemverGitRepository()
    with pytest.raises(ValueError):
        repo._find_packages_from_dep(Dependency("some-project", ">=1.0"))
