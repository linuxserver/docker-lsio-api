import lsio_github as gh
from keyvaluestore import KeyValueStore, set_db_schema
from models import Architecture, Changelog, Tag, Image, Repository, ImagesData, ImagesResponse, IMAGES_SCHEMA_VERSION

import datetime
import os
import time

CI = os.environ.get("CI", None)
INVALIDATE_HOURS = int(os.environ.get("INVALIDATE_HOURS", "24"))


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
    return description

def get_image(repo):
    if not repo.name.startswith("docker-") or repo.name.startswith("docker-baseimage-"):
        return None
    readme_vars = gh.get_readme_vars(repo)
    if not readme_vars:
        return None
    categories = readme_vars.get("project_categories", "")
    if "Internal" in categories:
        return None
    tags, stable = get_tags(readme_vars)
    deprecated = readme_vars.get("project_deprecation_status", False)
    version, version_timestamp = gh.get_last_stable_release(repo)
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

def update_images():
    with KeyValueStore(invalidate_hours=INVALIDATE_HOURS, readonly=False) as kv:
        is_updated = kv.update_schema("images", IMAGES_SCHEMA_VERSION)
        if ("images" in kv and is_updated) or CI == "1":
            print(f"{datetime.datetime.now()} - skipped - already updated")
            return
        print(f"{datetime.datetime.now()} - updating images")
        images = []
        repos = gh.get_repos()
        for repo in sorted(repos, key=lambda repo: repo.name):
            image = get_image(repo)
            if not image:
                continue
            images.append(image)
        new_state = ImagesResponse(status="OK", data=ImagesData(repositories=Repository(linuxserver=images))).model_dump_json()
        kv.set_value("images", new_state, IMAGES_SCHEMA_VERSION)
        print(f"{datetime.datetime.now()} - updated images")

def main():
    set_db_schema()
    while True:
        gh.print_rate_limit()
        update_images()
        gh.print_rate_limit()
        time.sleep(INVALIDATE_HOURS*60*60)

if __name__ == "__main__":
    main()
