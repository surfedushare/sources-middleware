import os
import json
import boto3

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo

from commands import TARGETS
from environments.project import REPOSITORY, REPOSITORY_AWS_PROFILE
from environments.utils.packaging import get_package_info


@task()
def prepare_builds(ctx):
    """
    Makes sure that repo information will be present inside Docker images
    """
    repo = Repo(".")
    commit = str(repo.head.commit)
    # TODO: we can make assertions about the git state like: no uncommited changes and no untracked files
    middleware_package = TARGETS["middleware"]
    info = {
        "commit": commit,
        "versions": {
            "middleware": middleware_package["version"]
        }
    }
    with open(os.path.join("environments", "info.json"), "w") as info_file:
        json.dump(info, info_file)


@task(prepare_builds, help={
    "version": "Version of the project you want to build. Must match value in package.py"
})
def build(ctx, version):
    """
    Uses Docker to build an image for a Django project
    """
    target = "middleware"
    package_info = get_package_info()
    package_version = package_info["versions"][target]
    if package_version != version:
        raise Exit(
            f"Expected version of {target} to match {version} instead it's {package_version}. Update package.py?",
            code=1
        )

    # Gather necessary info and call Docker to build
    target_info = TARGETS[target]
    ctx.run(
        f"docker build -f {target_info['directory']}/Dockerfile -t {target_info['name']}:{version} .",
        pty=True,
        echo=True
    )
    ctx.run(
        f"docker build -f nginx/Dockerfile-nginx -t {target_info['name']}-nginx:{version} .",
        pty=True,
        echo=True
    )


@task(help={
    "version": "Version of the project you want to push. Defaults to latest version"
})
def push(ctx, version=None):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """
    # Load info
    target_info = TARGETS["middleware"]
    version = version or target_info["version"]
    name = target_info["name"]

    # Login with Docker to AWS
    ctx.run(
        f"AWS_PROFILE={REPOSITORY_AWS_PROFILE} aws ecr get-login-password --region eu-central-1 | "
        f"docker login --username AWS --password-stdin {REPOSITORY}",
        echo=True
    )
    # Tag the main image and push
    ctx.run(f"docker tag {name}:{version} {REPOSITORY}/{name}:{version}", echo=True)
    ctx.run(f"docker push {REPOSITORY}/{name}:{version}", echo=True, pty=True)
    # Tag Nginx and push
    ctx.run(f"docker tag {name}-nginx:{version} {REPOSITORY}/{name}-nginx:{version}", echo=True)
    ctx.run(f"docker push {REPOSITORY}/{name}-nginx:{version}", echo=True, pty=True)


@task()
def print_available_images(ctx):

    # Load info
    target_info = TARGETS["middleware"]
    name = target_info["name"]

    # Start boto
    session = boto3.Session(profile_name="nppo-prod")
    ecr = session.client("ecr")

    # List images
    production_account = "870512711545"
    response = ecr.list_images(
        registryId=production_account,
        repositoryName=name,
    )

    # Print output
    def image_version_sort(image):
        return tuple([int(section) for section in image["imageTag"].split(".")])
    images = sorted(response["imageIds"], key=image_version_sort, reverse=True)
    print(json.dumps(images[:10], indent=4))
