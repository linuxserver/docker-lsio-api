from github import Auth
from github import Github

import os
import yaml

PAT = os.environ.get("PAT", None)
GH_AUTH = Auth.Token(PAT) if PAT else None
GH = Github(auth=GH_AUTH)

def get_repos():
    org = GH.get_organization("linuxserver")
    return org.get_repos()

def get_file(repo, branch, path, is_yaml=False):
    try:
        content = repo.get_contents(path, ref=branch).decoded_content
        return yaml.load(content, Loader=yaml.CLoader) if is_yaml else content
    except:
        return None

def get_last_stable_release(repo):
    for release in repo.get_releases():
        if release.prerelease:
            continue
        return release.tag_name, str(release.published_at)
    return "latest", str(repo.pushed_at)

def get_readme_vars(repo):
    return (
        get_file(repo, "master", "readme-vars.yml", is_yaml=True) or
        get_file(repo, "main", "readme-vars.yml", is_yaml=True) or
        get_file(repo, "develop", "readme-vars.yml", is_yaml=True) or
        get_file(repo, "nightly", "readme-vars.yml", is_yaml=True))

def print_rate_limit():
    print(f"Github ratelimit - {GH.get_rate_limit()}")
