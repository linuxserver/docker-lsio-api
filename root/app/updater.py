from github import Auth
from github import Github
from keyvaluestore import KeyValueStore

import datetime
import json
import os
import threading
import time
import yaml

CI = os.environ.get("CI", None)
INVALIDATE_HOURS = int(os.environ.get("INVALIDATE_HOURS", "24"))
PAT = os.environ.get("PAT", None)


def get_repos():
    auth = Auth.Token(PAT) if PAT else None
    gh = Github(auth=auth)
    org = gh.get_organization("linuxserver")
    repos = org.get_repos()
    return [repo for repo in repos if repo.full_name.startswith("linuxserver/docker-") 
            and not repo.full_name.startswith("linuxserver/docker-baseimage-") 
            and (repo.description is None or "DEPRECATED" not in repo.description)]

def get_vars(repo, branch):
    try:
        content = repo.get_contents("readme-vars.yml", ref=branch).decoded_content
        return yaml.load(content, Loader=yaml.CLoader)
    except:
        return None

def get_state():
    images = []
    repos = get_repos()
    for repo in sorted(repos, key=lambda repo: repo.full_name):
        readme_vars = get_vars(repo, "master") or get_vars(repo, "main") or get_vars(repo, "develop") or get_vars(repo, "nightly")
        if not readme_vars or "'project_deprecation_status': True" in str(readme_vars):
            continue
        categories = readme_vars.get("project_categories", "")
        if "Internal" in categories:
            continue
        version = "latest" if "development_versions_items" not in readme_vars else readme_vars["development_versions_items"][0]["tag"]
        images.append({
                    "name": repo.full_name.replace("linuxserver/docker-", ""),
                    "version": version,
                    "category": categories,
                    "stable": version == "latest",
                    "deprecated": False
                })
    return {"status": "OK", "data": {"repositories": {"linuxserver": images}}}

def update_images():
    with KeyValueStore(invalidate_hours=INVALIDATE_HOURS, readonly=False) as kv:
        if "images" in kv or CI == "1":
            print(f"{datetime.datetime.now()} - skipped - already updated")
            return
        print(f"{datetime.datetime.now()} - updating images")
        current_state = get_state()
        kv["images"] = json.dumps(current_state)
        print(f"{datetime.datetime.now()} - updated images")

class UpdateImages(threading.Thread):
    def run(self,*args,**kwargs):
        while True:
            update_images()
            time.sleep(INVALIDATE_HOURS*60*60)

if __name__ == "__main__":
    update_images_thread = UpdateImages()
    update_images_thread.start()
