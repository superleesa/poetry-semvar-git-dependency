import sys
from typing import TYPE_CHECKING

from poetry.plugins.plugin import Plugin
from poetry.core.packages.dependency_group import DependencyGroup

from poetry_semvar_git_dependency.core.packages.semvar_git_dependency import (
    SemvarGitDependency,
)
from poetry_semvar_git_dependency.repositories.semvar_git_repository import (
    SemvarGitRepository,
)
from poetry_semvar_git_dependency.core.constraints.version.parser import (
    is_sem_ver_constraint,
)

if TYPE_CHECKING:
    from poetry.plugins.plugin import Poetry
    from poetry.plugins.plugin import IO


class SemvarGitDependencyPlugin(Plugin):
    COMMANDS = [
        "add",
        "install",
        "lock",
        "sync",
        "update",
    ]

    def activate(self, poetry: Poetry, io: IO) -> None:
        # FIXME: i think there is a better way to do this...
        if len(sys.argv) > 1 and sys.argv[1] in SemvarGitDependencyPlugin.COMMANDS:
            self.override_semver_dependency(poetry, io)

    def override_semver_dependency(self, poetry: Poetry, io: IO) -> None:
        io.write_line("initial plugin activation")

        # TODO: only apply this for install / update / add

        repository_pool = poetry.pool
        updated_dependency_groups: dict[str, DependencyGroup] = {}
        found_semvar_tag = False

        for group_name, group_dep in poetry.package._dependency_groups.items():
            updated_deps = []
            for dep in group_dep.dependencies:
                if not dep.is_vcs():
                    updated_deps.append(dep)
                    continue

                if dep.source_reference is None or not is_sem_ver_constraint(
                    dep.source_reference
                ):
                    updated_deps.append(dep)
                    continue

                found_semvar_tag = True
                semvar_dep = SemvarGitDependency(
                    dep.name, dep.source_url, dep.source_reference
                )
                updated_deps.append(semvar_dep)

            group_dep._dependencies = updated_deps

        if found_semvar_tag:
            semvar_git_repo = SemvarGitRepository()
            repository_pool.add_repository(
                semvar_git_repo
            )  # this is used by all semvar git dependencies

        poetry.package._dependency_groups = updated_dependency_groups
