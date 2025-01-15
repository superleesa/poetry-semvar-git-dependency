import sys

from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry
from cleo.io.io import IO

from poetry_semver_git_dependency.core.packages.semver_git_dependency import (
    SemverGitDependency,
)
from poetry_semver_git_dependency.repositories.semver_git_repository import (
    SemverGitRepository,
)
from poetry_semver_git_dependency.core.constraints.version.parser import (
    is_sem_ver_constraint,
)


class SemverGitDependencyPlugin(Plugin):
    COMMANDS = [
        "add",
        "install",
        "lock",
        "sync",
        "update",
    ]

    def activate(self, poetry: Poetry, io: IO) -> None:
        # FIXME: i think there is a better way to do this...
        if len(sys.argv) > 1 and sys.argv[1] in SemverGitDependencyPlugin.COMMANDS:
            self.override_semver_dependency(poetry, io)

    def override_semver_dependency(self, poetry: Poetry, io: IO) -> None:
        io.write_line("Overriding semver git dependencies...")

        # patch dependency if it is a semver git dependency
        found_semver_tag = False
        for group_name, group_dep in poetry.package._dependency_groups.items():
            updated_deps = []
            for dep in group_dep.dependencies:
                if (
                    not dep.is_vcs()
                    or dep.source_reference is None
                    or dep.source_url is None
                    or not is_sem_ver_constraint(dep.source_reference)
                ):
                    updated_deps.append(dep)
                    continue

                found_semver_tag = True
                semver_dep = SemverGitDependency(
                    dep.name, dep.source_url, dep.source_reference
                )
                updated_deps.append(semver_dep)

            group_dep._dependencies = updated_deps

        # add semver git repository if semver git dependency is found
        if found_semver_tag:
            semver_git_repo = SemverGitRepository()
            poetry.pool.add_repository(
                semver_git_repo
            )  # this is used by all semver git dependencies
