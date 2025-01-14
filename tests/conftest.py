import tempfile
import shutil
from pathlib import Path
from typing import Any, Generator

import pytest
from dulwich.repo import Repo

from tests.helpers import create_file_and_tag_commit

PYPROJECT_V1_0 = (Path(__file__).parent / "data" / "pyproject_v1_0.toml").read_text(
    encoding="utf-8"
)
PYPROJECT_V2_0_1 = (Path(__file__).parent / "data" / "pyproject_v2_0_1.toml").read_text(
    encoding="utf-8"
)
PYPROJECT_V2_1_1 = (Path(__file__).parent / "data" / "pyproject_v2_1_1.toml").read_text(
    encoding="utf-8"
)


@pytest.fixture(scope="session")
def mock_git_repo() -> Generator[Repo, Any, None]:
    # create temp path
    repo_path = tempfile.mkdtemp()
    # repo_path = str(Path(r"C:\Users\super\Documents\8.workspace\practice_poetry_plugin\dump"))
    repo = Repo.init(repo_path)

    tags = ["1.0", "1.1", "2.0"]
    pyprojects = [PYPROJECT_V1_0, PYPROJECT_V2_0_1, PYPROJECT_V2_1_1]
    for tag_name, pyproject in zip(tags, pyprojects):
        create_file_and_tag_commit(pyproject, "pyproject.toml", tag_name, repo)

    yield repo

    shutil.rmtree(repo_path)
