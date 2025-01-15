from unittest.mock import Mock

import pytest
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.vcs_dependency import VCSDependency

from poetry_semver_git_dependency.core.packages.semver_git_dependency import (
    SemverGitDependency,
)
from poetry_semver_git_dependency.plugin import SemverGitDependencyPlugin
from tests.mock_constants import (
    MOCK_PROJECT_FILE_PATH,
    MOCK_GIT_SOURCE_URL,
    MOCK_DEPENDENCY_NAME,
)
from tests.helpers import FakePoetry, create_project_package_from_raw_dep_groups


SEMVER_TAG_GIT_DEP = VCSDependency(
    name=MOCK_DEPENDENCY_NAME.format(dep_id=0),
    vcs="git",
    source=MOCK_GIT_SOURCE_URL,
    tag=">=1.0",
)
FORMATTED_SEMVER_GIT_DEPENDENCY = SemverGitDependency(
    name=MOCK_DEPENDENCY_NAME.format(dep_id=0),
    source_url=MOCK_GIT_SOURCE_URL,
    semver_tag=">=1.0",
)
NON_SEMVER_TAG_GIT_DEP = VCSDependency(
    name=MOCK_DEPENDENCY_NAME.format(dep_id=1),
    vcs="git",
    source=MOCK_GIT_SOURCE_URL,
    tag="some-tag",
)
BRANCH_GIT_DEP = VCSDependency(
    name=MOCK_DEPENDENCY_NAME.format(dep_id=2),
    vcs="git",
    source=MOCK_GIT_SOURCE_URL,
    branch="main",
)
OTHER_DEP = Dependency(name=MOCK_DEPENDENCY_NAME.format(dep_id=3), constraint=">=1.0")


@pytest.mark.parametrize(
    ("poetry", "expected_poetry"),
    [
        (  # git dep with semver tag replaced with SemverGitDependency
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {MAIN_GROUP: [SEMVER_TAG_GIT_DEP]}
                ),
            ),
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {MAIN_GROUP: [FORMATTED_SEMVER_GIT_DEPENDENCY]}
                ),
            ),
        ),
        (  # git dep without semver tag not replaced
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {MAIN_GROUP: [NON_SEMVER_TAG_GIT_DEP]}
                ),
            ),
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {MAIN_GROUP: [NON_SEMVER_TAG_GIT_DEP]}
                ),
            ),
        ),
        (  # git with revision / branch not replaced
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {MAIN_GROUP: [BRANCH_GIT_DEP]}
                ),
            ),
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {MAIN_GROUP: [BRANCH_GIT_DEP]}
                ),
            ),
        ),
        (  # other non-vcs dependencies not replaced
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups({MAIN_GROUP: [OTHER_DEP]}),
            ),
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups({MAIN_GROUP: [OTHER_DEP]}),
            ),
        ),
        (  # semver tag git dependency in other than MAIN group should also be replaced
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {"other-group": [SEMVER_TAG_GIT_DEP]}
                ),
            ),
            FakePoetry(
                MOCK_PROJECT_FILE_PATH,
                create_project_package_from_raw_dep_groups(
                    {"other-group": [FORMATTED_SEMVER_GIT_DEPENDENCY]}
                ),
            ),
        ),
    ],
)
def test_override_semver_dependency(poetry: FakePoetry, expected_poetry: FakePoetry) -> None:
    io = Mock()
    SemverGitDependencyPlugin().override_semver_dependency(poetry, io)
    
    for (actual_group_dep_name, actual_group_dep), (
        expected_group_dep_name,
        expected_group_dep,
    ) in zip(
        poetry.package._dependency_groups.items(),
        expected_poetry.package._dependency_groups.items(),
    ):
        assert actual_group_dep_name == expected_group_dep_name
        assert set(actual_group_dep.dependencies) == set(
            expected_group_dep.dependencies
        )
