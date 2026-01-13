"File containing helper functions for ingesting and cleaning content from Git repositories"

import git
import os
import subprocess
import time
import hashlib
import db

def clone_repository(repo_url: str):
    """
    Clone a Git repository to a local directory
    """
    subprocess.run(["git", "clone", repo_url])