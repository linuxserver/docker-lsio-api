from github import Auth
from github import Github

import os
import yaml

PAT = os.environ.get("PAT", None)


def get_repos():
    auth = Auth.Token(PAT) if PAT else None
    gh = Github(auth=auth)
    org = gh.get_organization("linuxserver")
    repos = org.get_repos()
    return [repo for repo in sorted(repos, key=lambda repo: repo.name) if repo.name.startswith("docker-") 
            and not repo.name.startswith("docker-baseimage-") 
            and (repo.description is None or "DEPRECATED" not in repo.description)]

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
    master = get_file(repo, "master", "readme-vars.yml", is_yaml=True)
    main = get_file(repo, "master", "readme-vars.yml", is_yaml=True)
    develop = get_file(repo, "master", "readme-vars.yml", is_yaml=True)
    nightly = get_file(repo, "master", "readme-vars.yml", is_yaml=True)
    return master or main or develop or nightly
