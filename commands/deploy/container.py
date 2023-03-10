import os
import json
import boto3

from invoke import Exit
from invoke.tasks import task
from git import Repo

from commands import TARGETS
from commands.aws import ENVIRONMENT_NAMES_TO_CODES
from environments.project import REPOSITORY, REPOSITORY_AWS_PROFILE


def get_commit_hash():
    repo = Repo(".")
    return str(repo.head.commit)


def aws_docker_login(ctx):
    command = f"aws ecr get-login-password --region eu-central-1 | " \
              f"docker login --username AWS --password-stdin {REPOSITORY}"
    if os.environ.get("AWS_PROFILE", None):
        command = f"AWS_PROFILE={REPOSITORY_AWS_PROFILE} " + command
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
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session"
})
def build(ctx, commit=None, docker_login=False):
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
    latest_remote_image = f"{REPOSITORY}/{name}:latest"
    ctx.run(
        f"DOCKER_BUILDKIT=1 docker build "
        f"--build-arg BUILDKIT_INLINE_CACHE=1 --cache-from {latest_remote_image} --progress=plain "
        f"--platform=linux/amd64 -f api/Dockerfile -t {name}:{commit} .",
        pty=True,
        echo=True
    )
    ctx.run(
        f"docker build --platform=linux/amd64 -f nginx/Dockerfile-nginx -t {name}-nginx:{commit} .",
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

    # Load info
    target_info = TARGETS["middleware"]
    name = target_info["name"]

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Check if commit tag already exists in registry
    push_commit_tag = True
    inspection = ctx.run(f"docker manifest inspect {REPOSITORY}/{name}:{commit}", warn=True)
    if inspection.exited == 0:
        print("Can't push commit tag that already has an image in the registry. Skipping.")
        push_commit_tag = False

    # Tagging and pushing of our image and nginx image
    tags = [commit] if push_commit_tag else []
    if push_latest:
        tags.append("latest")
    for tag in tags:
        ctx.run(f"docker tag {name}:{commit} {REPOSITORY}/{name}:{tag}", echo=True)
        ctx.run(f"docker push {REPOSITORY}/{name}:{tag}", echo=True, pty=True)
        ctx.run(f"docker tag {name}-nginx:{commit} {REPOSITORY}/{name}-nginx:{tag}", echo=True)
        ctx.run(f"docker push {REPOSITORY}/{name}-nginx:{tag}", echo=True, pty=True)


@task(help={
    "commit": "The commit hash that the image to be promoted is tagged with",
    "docker_login": "Specify this flag to login to AWS registry. Needed only once per session",
    "version": "Which version to promote. Defaults to version specified in package.py."
})
def promote(ctx, commit=None, docker_login=False, version=None):
    """
    Pushes a previously made Docker image to the AWS container registry, that's shared between environments
    """
    # Check the input for validity
    if commit and version:
        raise Exit("Can't promote a version and commit at the same time.")
    if ctx.config.env not in ENVIRONMENT_NAMES_TO_CODES:
        raise Exit(f"Can't promote for {ctx.config.env} environment")

    # Load info variables
    target_info = TARGETS["middleware"]
    name = target_info["name"]
    commit = commit or get_commit_hash()
    is_version_promotion = bool(version)

    # Prepare promote
    version = version or target_info["version"]
    promote_tags = [ENVIRONMENT_NAMES_TO_CODES[ctx.config.env], version]
    source_tag = version if is_version_promotion else commit

    # Login with Docker on AWS
    if docker_login:
        aws_docker_login(ctx)

    # Check if version tag already exists in registry
    inspection = ctx.run(f"docker manifest inspect {REPOSITORY}/{name}:{version}", warn=True)
    version_exists = inspection.exited == 0
    if version_exists:
        print("Skipping version tagging, because version already exists in registry")
        promote_tags.pop()

    # Print some output to know what the command is going to do
    print("Source tag:", source_tag)
    print("Tags added by promotion:", promote_tags)

    # Pull the source images
    ctx.run(f"docker pull {REPOSITORY}/{name}:{source_tag}", echo=True, pty=True)
    ctx.run(f"docker pull {REPOSITORY}/{name}-nginx:{source_tag}", echo=True, pty=True)

    # Tagging and pushing of our image and nginx image with relevant tags
    for promote_tag in promote_tags:
        ctx.run(f"docker tag {REPOSITORY}/{name}:{source_tag} {REPOSITORY}/{name}:{promote_tag}", echo=True)
        ctx.run(f"docker push {REPOSITORY}/{name}:{promote_tag}", echo=True, pty=True)
        ctx.run(f"docker tag {REPOSITORY}/{name}-nginx:{source_tag} {REPOSITORY}/{name}-nginx:{promote_tag}", echo=True)
        ctx.run(f"docker push {REPOSITORY}/{name}-nginx:{promote_tag}", echo=True, pty=True)


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
