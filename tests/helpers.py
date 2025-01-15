from unittest.mock import Mock

from pathlib import Path

from dulwich.repo import Repo
from dulwich.porcelain import tag_create, commit, add
from poetry.poetry import Poetry
from poetry.core.packages.project_package import ProjectPackage
from poetry.core.packages.dependency_group import DependencyGroup
from poetry.core.packages.dependency import Dependency

from tests.mock_constants import MOCK_PROJECT_NAME, MOCK_PROJECT_VERSION


def create_file_and_tag_commit(
    blob_text: str,
    entry_path: str,
    tag_name: str,
    repo: Repo,
    author_name="Mock User <mockuser@gmail.com>",
) -> None:
    full_entry_path = str(Path(repo.path) / entry_path)
    with open(full_entry_path, "w") as f:
        f.write(blob_text)
    add(repo, full_entry_path)
    commit_id: bytes = commit(
        repo,
        author=author_name,
        message=f"Mock commit for tag {tag_name}",
    )
    tag_create(
        repo=repo,
        tag=tag_name.encode(),
        annotated=True,
        author=author_name.encode(),
        objectish=commit_id,
        message=f"Mock tag {tag_name}".encode(),
    )


class FakePoetry(Poetry):
    """
    This assumes that we are not interested in configs / lockers
    """
    def __init__(self, file: Path, package: ProjectPackage) -> None:
        mock_config = Mock()
        mock_locker = Mock()
        super().__init__(file, {}, package, mock_locker, mock_config)


def create_project_package_from_raw_dep_groups(
    raw_dep_groups: dict[str, list[Dependency]],
) -> ProjectPackage:
    dep_groups = create_dep_groups_from_raw_group_deps(raw_dep_groups)
    project_package = ProjectPackage(MOCK_PROJECT_NAME, MOCK_PROJECT_VERSION)
    for group_name, group in dep_groups.items():
        project_package.add_dependency_group(group)
    return project_package


def create_dep_groups_from_raw_group_deps(
    deps: dict[str, list[Dependency]],
) -> dict[str, DependencyGroup]:
    dep_groups = {}
    for group_name, group_deps in deps.items():
        group = DependencyGroup(name=group_name)
        for dep in group_deps:
            group.add_dependency(dep)
        dep_groups[group_name] = group
    return dep_groups
