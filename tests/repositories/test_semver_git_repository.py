from unittest.mock import Mock

import pytest
from dulwich.repo import Repo
from poetry.core.packages.package import Package

from poetry_semver_git_dependency.core.packages.semver_git_dependency import (
    SemverGitDependency,
)
from poetry_semver_git_dependency.repositories.semver_git_repository import (
    SemverGitRepository,
)


@pytest.mark.parametrize(
    ("semver_git_dep", "expected_packages"),
    [
        (
            SemverGitDependency(
                "mock-project", "https://github.com/mock-project", ">=1.0"
            ),
            [
                Package(
                    "mock-project",
                    "1.0.0",
                    source_type="git",
                    source_url="https://github.com/mock-project",
                    source_reference="1.0.0",
                ),
                Package(
                    "mock-project",
                    "2.0.1",
                    source_type="git",
                    source_url="https://github.com/mock-project",
                    source_reference="2.0.1",
                ),
                Package(
                    "mock-project",
                    "2.1.1",
                    source_type="git",
                    source_url="https://github.com/mock-project",
                    source_reference="2.1.1",
                ),
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
