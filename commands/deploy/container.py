import os
import json
import boto3

from invoke.tasks import task
from invoke.exceptions import Exit
from git import Repo

from commands import TARGETS


def get_commit_hash():
    repo = Repo(".")
    return str(repo.head.commit)


def aws_docker_login(ctx):
    command = f"aws ecr get-login-password --region eu-central-1 | " \
              f"docker login --username AWS --password-stdin {ctx.config.aws.production.registry}"
    if os.environ.get("AWS_PROFILE", None):
        command = f"AWS_PROFILE={ctx.config.aws.production.profile_name} " + command
        ctx.run(command)
    ctx.run(command, echo=True)


@task(help={
    "commit": "The commit hash a new build should include in its info.json"
})
def prepare_builds(ctx, commit=None):
    """
    Makes sure that repo information will be present inside Docker images
    """
    commit = commit or get_commit_hash()
    middleware_package = TARGETS["middleware"]
    info = {
        "commit": commit,
        "versions": {
            "middleware": middleware_package["version"]
        }
    }
    with open(os.path.join("environments", "info.json"), "w") as info_file:
        json.dump(info, info_file)


@task(help={
    "commit": "The commit hash a new build should include in its info.json. Will also be used to tag the new image.",
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session.",
    "no_cache": "Add this flag to make a build without cached layers."
})
def build(ctx, commit=None, docker_login=False, no_cache=False):
    """
    Uses Docker to build an image for a Django project
    """
    commit = commit or get_commit_hash()

    prepare_builds(ctx, commit)

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Gather necessary info and call Docker to build
    target_info = TARGETS["middleware"]
    name = target_info['name']
    no_cache_flag = "--no-cache" if no_cache else ""
    ctx.run(
        f"docker build "
        f"--progress=plain "
        f"--platform=linux/amd64 -f api/Dockerfile -t {name}:{commit} . {no_cache_flag}",
        pty=True,
        echo=True
    )
    ctx.run(
        f"docker build --platform=linux/amd64 -f nginx/Dockerfile-nginx -t {name}-nginx:{commit} . {no_cache_flag}",
        pty=True,
        echo=True
    )


@task(help={
    "commit": "The commit hash that the image to be pushed is tagged with.",
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session",
    "push_latest": "Makes the command push a latest tag to use these layers later."
})
def push(ctx, commit=None, docker_login=False, push_latest=False):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """
    commit = commit or get_commit_hash()
    registry = ctx.config.aws.production.registry

    # Load info
    target_info = TARGETS["middleware"]
    name = target_info["name"]

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Check if commit tag already exists in registry
    push_commit_tag = True
    inspection = ctx.run(f"docker manifest inspect {registry}/{name}:{commit}", warn=True)
    if inspection.exited == 0:
        print("Can't push commit tag that already has an image in the registry. Skipping.")
        push_commit_tag = False

    # Tagging and pushing of our image and nginx image
    tags = [commit] if push_commit_tag else []
    if push_latest:
        tags.append("latest")
    for tag in tags:
        ctx.run(f"docker tag {name}:{commit} {registry}/{name}:{tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}:{tag}", echo=True, pty=True)
        ctx.run(f"docker tag {name}-nginx:{commit} {registry}/{name}-nginx:{tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}-nginx:{tag}", echo=True, pty=True)


@task(
    help={
        "commit": "The commit hash that the image to be promoted is tagged with",
        "docker_login": "Specify this flag to login to AWS registry. Needed only once per session",
        "version": "Which version to promote. Defaults to version specified in package.py.",
        "exclude": "List deploy targets that you want to exclude from this deploy like: "
                   "edusources, publinova or central",
    },
    iterable=["exclude"]
)
def promote(ctx, commit=None, docker_login=False, version=None, exclude=None):
    """
    Adds deploy tags to a previously pushed Docker image in the AWS container registry.
    """
    # Check the input for validity
    if commit and version:
        raise Exit("Can't promote a version and commit at the same time.")
    if ctx.config.service.env == "localhost":
        raise Exit("Can't promote for localhost environment")

    # Load info variables
    target_info = TARGETS["middleware"]
    name = target_info["name"]
    commit = commit or get_commit_hash()
    is_version_promotion = bool(version)

    # Prepare promote
    registry = ctx.config.aws.production.registry
    version = version or target_info["version"]
    deploy_tags = dict(**ctx.config.service.deploy.tags)
    for exclusion in exclude:
        deploy_tags.pop(exclusion, None)
    if not deploy_tags:
        raise Exit("Not a single deploy target selected")
    promote_tags = list(deploy_tags.values()) + [version]
    source_tag = version if is_version_promotion else commit

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Check if version tag already exists in registry
    inspection = ctx.run(f"docker manifest inspect {registry}/{name}:{version}", warn=True)
    version_exists = inspection.exited == 0
    if version_exists:
        print("Skipping version tagging, because version already exists in registry")
        promote_tags.pop()

    # Print some output to know what the command is going to do
    print("Source tag:", source_tag)
    print("Tags added by promotion:", promote_tags)

    # Pull the source images
    ctx.run(f"docker pull {registry}/{name}:{source_tag}", echo=True, pty=True)
    ctx.run(f"docker pull {registry}/{name}-nginx:{source_tag}", echo=True, pty=True)

    # Tagging and pushing of our image and nginx image with relevant tags
    for promote_tag in promote_tags:
        ctx.run(f"docker tag {registry}/{name}:{source_tag} {registry}/{name}:{promote_tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}:{promote_tag}", echo=True, pty=True)
        ctx.run(f"docker tag {registry}/{name}-nginx:{source_tag} {registry}/{name}-nginx:{promote_tag}", echo=True)
        ctx.run(f"docker push {registry}/{name}-nginx:{promote_tag}", echo=True, pty=True)


@task()
def print_available_images(ctx):
    """
    Retrieves some images from AWS and prints them in version order.
    Possibly misses versions if it's not part of the first images batch from AWS.
    """
    # Load info
    target_info = TARGETS["middleware"]
    name = target_info["name"]

    # Start boto
    session = boto3.Session(profile_name=ctx.config.aws.production.profile_name)
    ecr = session.client("ecr")

    # List images
    production_account = ctx.config.aws.production.account
    response = ecr.list_images(
        registryId=production_account,
        repositoryName=name,
    )

    # Print output
    def image_version_sort(image):
        return tuple([int(section) for section in image["imageTag"].split(".")])
    images = [image for image in response["imageIds"] if "imageTag" in image and "." in image["imageTag"]]
    images.sort(key=image_version_sort, reverse=True)
    print(json.dumps(images[:10], indent=4))
