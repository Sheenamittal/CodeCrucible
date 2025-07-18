# core/git_handler.py

import git
import shutil
import os
from rich.console import Console
from rich.progress import Progress

console = Console()

class CloneProgress(git.remote.RemoteProgress):
    """A progress handler for GitPython that uses rich.progress."""
    def __init__(self, progress_bar: Progress, task_id):
        super().__init__()
        self.pbar = progress_bar
        self.task_id = task_id

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.update(self.task_id, total=max_count, completed=cur_count, description=f"[cyan]{message}")

def clone_repo(url: str, path: str = "temp_repo") -> bool:
    """
    Clones a public GitHub repository using a shallow clone and skipping LFS files.
    """
    if os.path.exists(path):
        console.log(f"Removing existing directory at '{path}'...")
        shutil.rmtree(path)

    console.log(f"Cloning repository from '{url}' into '{path}'...")
    
    clone_env = os.environ.copy()
    clone_env["GIT_LFS_SKIP_SMUDGE"] = "1"

    with Progress() as progress:
        task = progress.add_task("[cyan]Cloning...", total=None)
        try:
            git.Repo.clone_from(
                url,
                path,
                depth=1,
                progress=CloneProgress(progress, task),
                env=clone_env
            )
            progress.update(task, description="[bold green]Repository cloned successfully.[/bold green]")
            return True
        except git.exc.GitCommandError as e:
            progress.update(task, description="[bold red]Error: Failed to clone.[/bold red]")
            console.print(f"Details: {e}")
            return False