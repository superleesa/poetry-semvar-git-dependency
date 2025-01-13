from typing import TYPE_CHECKING
from poetry.plugins.plugin import Plugin

if TYPE_CHECKING:
    from poetry.plugins.plugin import Poetry
    from poetry.plugins.plugin import IO


class SemvarGitDependencyPlugin(Plugin):
    def activate(self, poetry: Poetry, io: IO) -> None:
        io.write_line("initial plugin activation")
