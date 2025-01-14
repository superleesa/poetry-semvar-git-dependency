from pathlib import Path
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit, Tag
from dulwich.porcelain import tag_create, commit, add

DEFAULT_PERMISSIONS = 0o100644



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
    commit_id: bytes = commit(repo, author=author_name, message=f"Mock commit for tag {tag_name}",)
    tag_create(repo=repo, tag=tag_name.encode(), annotated=True, author=author_name.encode(), objectish=commit_id, message=f"Mock tag {tag_name}".encode(),)
