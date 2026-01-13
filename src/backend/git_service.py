"""Helper functions for ingesting content from Git repositories via GitHub API"""

import requests

GITHUB_API_BASE = "https://api.github.com"

SKIP_DIRECTORIES = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "vendor",
    ".idea",
    ".vscode",
}

SKIP_FILES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tiff",
    ".ico",
    ".webp",
    ".yaml",
    ".yml",
    ".lock",
    ".env",
    ".gitignore",
}

def parse_github_url(repo_url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL.
    
    'https://github.com/owner/repo' -> ('owner', 'repo')
    """

    url_split = repo_url.rstrip("/").split("/")
    if len(url_split) < 2:
        raise ValueError("Invalid GitHub URL")
    return url_split[-2], url_split[-1]


def fetch_repo_contents(owner: str, repo: str, path: str = "") -> list:
    """Fetch list of files/folders at a given path in the repo.
    
    Calls: GET /repos/{owner}/{repo}/contents/{path}
    """

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_file_content(download_url: str) -> str:
    """Download the raw content of a single file."""

    if not download_url:
        return None
    try:
        response = requests.get(download_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file content from {download_url}: {e}")
        return None

def should_ingest_file(filename: str) -> bool:
    """Return True if this file should be ingested (skip images, binaries, etc.)."""
    
    if filename.endswith(tuple(SKIP_FILES)):
        return False
    return True

def should_skip_directory(dir_name: str) -> bool:
    """Return True if this directory should be skipped."""
    return dir_name in SKIP_DIRECTORIES