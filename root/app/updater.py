from github import Github
from keyvaluestore import KeyValueStore
from urllib.request import urlopen

import datetime
import json
import os
import threading
import time
import yaml

INVALIDATE_HOURS = int(os.environ.get("INVALIDATE_HOURS", "24"))


def get_repos():
    gh = Github()
    org = gh.get_organization("linuxserver")
    repos = org.get_repos()
    return [repo.full_name for repo in repos if repo.full_name.startswith("linuxserver/docker-") 
            and not repo.full_name.startswith("linuxserver/docker-baseimage-") 
            and (repo.description is None or "DEPRECATED" not in repo.description)]

def get_vars(repo, branch):
    try:
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/readme-vars.yml"
        content = urlopen(url).read()
        return yaml.load(content, Loader=yaml.CLoader)
    except:
        return None

def get_state():
    images = []
    repos = get_repos()
    for repo in sorted(repos):
        readme_vars = get_vars(repo, "master") or get_vars(repo, "main") or get_vars(repo, "develop") or get_vars(repo, "nightly")
        if not readme_vars or "'project_deprecation_status': True" in str(readme_vars):
            continue
        version = "latest" if "development_versions_items" not in readme_vars else readme_vars["development_versions_items"][0]["tag"]
        images.append({
                    "name": repo.replace("linuxserver/docker-", ""),
                    "version": version,
                    "category": readme_vars.get("project_categories", ""),
                    "stable": version == "latest",
                    "deprecated": False
                })
    return {"status": "OK", "data": {"repositories": {"linuxserver": images}}}

def update_images():
    with KeyValueStore(invalidate_hours=INVALIDATE_HOURS, readonly=False) as kv:
        if 'images' in kv:
            print(f'{datetime.datetime.now()} - skipped - already updated')
            return
        print(f'{datetime.datetime.now()} - updating images')
        current_state = get_state()
        kv['images'] = json.dumps(current_state)
        print(f'{datetime.datetime.now()} - updated images')

class UpdateImages(threading.Thread):
    def run(self,*args,**kwargs):
        while True:
            update_images()
            time.sleep(INVALIDATE_HOURS*60*60)

if __name__ == '__main__':
    update_images_thread = UpdateImages()
    update_images_thread.start()
