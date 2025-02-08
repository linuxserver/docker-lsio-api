from github import Auth
from github import Github
from keyvaluestore import KeyValueStore
from models import Architecture, Changelog, Tag, Image, Repository, ImagesData, SCHEMA_VERSION

import datetime
import json
import os
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
    return [repo for repo in repos if repo.name.startswith("docker-") 
            and not repo.name.startswith("docker-baseimage-") 
            and (repo.description is None or "DEPRECATED" not in repo.description)]

def get_vars(repo, branch):
    try:
        content = repo.get_contents("readme-vars.yml", ref=branch).decoded_content
        return yaml.load(content, Loader=yaml.CLoader)
    except:
        return None

def get_version(repo):
    for release in repo.get_releases():
        if release.prerelease:
            continue
        return release.tag_name, str(release.published_at)
    return "latest", str(repo.pushed_at)

def get_tags(readme_vars):
    if "development_versions_items" not in readme_vars:
        return [Tag(tag="latest", desc="Stable releases")], True
    tags = []
    stable = False
    for item in readme_vars["development_versions_items"]:
        if item["tag"] == "latest":
            stable = True
        tags.append(Tag(tag=item["tag"], desc=item["desc"]))
    return tags, stable

def get_architectures(readme_vars):
    if "available_architectures" not in readme_vars:
        return [Architecture(arch="arch_x86_64", tag="amd64-latest")]
    archs = []
    for item in readme_vars["available_architectures"]:
        archs.append(Architecture(arch=item["arch"][8:-3], tag=item["tag"]))
    return archs

def get_changelogs(readme_vars):
    if "changelogs" not in readme_vars:
        return [Changelog(date="01.01.50", desc="No changelog")]
    changelogs = []
    for item in readme_vars["changelogs"][0:3]:
        changelogs.append(Changelog(date=item["date"][0:-1], desc=item["desc"]))
    return changelogs

def get_description(readme_vars):
    description = readme_vars.get("project_blurb", "No description")
    description = description.replace("\n", " ").strip(" \t\n\r")
    if "project_name" in readme_vars:
        description = description.replace("[{{ project_name|capitalize }}]", readme_vars["project_name"])
        description = description.replace("[{{ project_name }}]", readme_vars["project_name"])
    if "project_url" in readme_vars:
        description = description.replace("({{ project_url }})", "")
    return json.dumps(description).replace("\"", "")

def get_image(repo):
    readme_vars = get_vars(repo, "master") or get_vars(repo, "main") or get_vars(repo, "develop") or get_vars(repo, "nightly")
    if not readme_vars:
        return None
    categories = readme_vars.get("project_categories", "")
    if "Internal" in categories:
        return None
    tags, stable = get_tags(readme_vars)
    deprecated = readme_vars.get("project_deprecation_status", False)
    version, version_timestamp = get_version(repo)
    return Image(
        name=repo.name.replace("docker-", ""),
        github_url=repo.html_url,
        project_url=readme_vars.get("project_url", ""),
        description=get_description(readme_vars),
        version=version,
        version_timestamp=version_timestamp,
        changelog=get_changelogs(readme_vars),
        category=categories,
        stable=stable,
        deprecated=deprecated,
        stars=repo.stargazers_count,
        tags=tags,
        architectures=get_architectures(readme_vars)
    )

def get_state():
    images = []
    repos = get_repos()
    for repo in sorted(repos, key=lambda repo: repo.name):
        image = get_image(repo)
        if not image:
            continue
        images.append(image)
    return ImagesData(repositories=Repository(linuxserver=images)).model_dump_json()

def update_images(schema_updated):
    with KeyValueStore(invalidate_hours=INVALIDATE_HOURS, readonly=False) as kv:
        if ("images" in kv and not schema_updated) or CI == "1":
            print(f"{datetime.datetime.now()} - skipped - already updated")
            return
        print(f"{datetime.datetime.now()} - updating images")
        kv["images"] = get_state()
        print(f"{datetime.datetime.now()} - updated images")

def update_schema():
    with KeyValueStore(invalidate_hours=0, readonly=False) as kv:
        if "schema_version" in kv and kv["schema_version"] == SCHEMA_VERSION:
            return False
        kv["schema_version"] = SCHEMA_VERSION
        return True

def main():
    while True:
        schema_updated = update_schema()
        update_images(schema_updated)
        time.sleep(INVALIDATE_HOURS*60*60)

if __name__ == "__main__":
    main()
