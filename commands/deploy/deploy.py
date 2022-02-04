import json
import boto3
from time import sleep

from invoke.tasks import task
from invoke.exceptions import Exit

from environments.project import MODE
from commands import TARGETS
from commands.aws.ecs import register_task_definition, build_default_container_variables, list_running_containers
from commands.aws.utils import create_aws_session


def register_scheduled_tasks(ctx, aws_config, task_definition_arn):
    session = create_aws_session(ctx.config.aws.profile_name)
    events_client = session.client('events')
    iam = session.resource('iam')
    role = iam.Role('ecsEventsRole')
    ecs_parameters = {
        'TaskDefinitionArn': task_definition_arn,
        'TaskCount': 1,
        'LaunchType': 'FARGATE',
        'NetworkConfiguration': {
            "awsvpcConfiguration": {
                "Subnets": [aws_config.private_subnet_id],
                "SecurityGroups": [
                    aws_config.rds_security_group_id,
                    aws_config.default_security_group_id

                ]
            }
        }
    }
    scheduled_tasks = [
        (task, str(ix+1), ["python", "manage.py", task])
        for ix, task in enumerate(ctx.config.aws.scheduled_tasks)
    ]
    for rule, identifier, command in scheduled_tasks:
        events_client.put_targets(
            Rule=rule,
            Targets=[
                {
                    'Id': identifier,
                    'Arn': aws_config.cluster_arn,
                    'RoleArn': role.arn,
                    'Input': json.dumps(
                        {
                            "containerOverrides": [
                                {
                                    "name": "search-portal-container",
                                    "command": command
                                }
                            ]
                        }
                    ),
                    'EcsParameters': ecs_parameters
                }
            ]
        )


def deploy_middleware(ctx, mode, ecs_client, task_role_arn, version):
    target_info = TARGETS["middleware"]
    container_variables = build_default_container_variables(mode, version)

    task_definition_arn = register_task_definition(
        "middleware",
        ecs_client,
        task_role_arn,
        container_variables,
        True,
        target_info["cpu"],
        target_info["memory"]
    )

    ecs_client.update_service(
        cluster=ctx.config.aws.cluster_arn,
        service="middleware",
        taskDefinition=task_definition_arn
    )


@task(help={
    "mode": "Mode you want to deploy to: development, acceptance or production. Must match APPLICATION_MODE",
    "version": "Version of the project you want to deploy. Defaults to latest version"
})
def deploy(ctx, mode, version=None):
    """
    Updates the container cluster in development, acceptance or production environment on AWS to run a Docker image
    """
    target = "middleware"

    print(f"Starting deploy of {target}")

    target_info = TARGETS[target]
    version = version or target_info["version"]
    task_role_arn = ctx.config.aws.task_role_arn

    print(f"Starting AWS session for: {mode}")
    ecs_client = create_aws_session(ctx.config.aws.profile_name).client('ecs', )

    print(f"Deploying version {version}")
    deploy_middleware(ctx, mode, ecs_client, task_role_arn, version)

    print("Waiting for deploy to finish ...")
    while True:
        running_containers = list_running_containers(ecs_client, ctx.config.aws.cluster_arn, target_info["name"])
        versions = set([container["version"] for container in running_containers])
        if len(versions) == 1 and version in versions:
            break
        sleep(10)
    print("Done deploying")


@task(help={
    "mode": "Mode you want to list versions for: development, acceptance or production. Must match APPLICATION_MODE",
})
def print_running_containers(ctx, mode):
    # Check the input for validity
    if mode != MODE:
        raise Exit(f"Expected mode to match APPLICATION_MODE value but found: {mode}", code=1)

    # Load info
    target_info = TARGETS["middleware"]
    name = target_info["name"]

    # Start boto
    session = boto3.Session(profile_name=ctx.config.aws.profile_name)
    ecs = session.client("ecs")

    # List images
    running_containers = list_running_containers(ecs, ctx.config.aws.cluster_arn, name)
    print(json.dumps(running_containers, indent=4))
