import boto3
from time import sleep

from invoke.tasks import task

from environments.project import FARGATE_CLUSTER_NAME


def await_steady_fargate_services(ecs_client, services):
    steady_services = {service: False for service in services}
    sleep(30)
    while not all(steady_services.values()):
        fargate_state = ecs_client.describe_services(cluster=FARGATE_CLUSTER_NAME, services=services)
        for service in fargate_state["services"]:
            last_event = next(iter(service["events"]), None)
            if not last_event:
                continue
            if "has reached a steady state" in last_event["message"]:
                steady_services[service["serviceName"]] = True
        sleep(10)


@task(help={
    "mode": "Mode you want to deploy to: development, acceptance or production. Must match APPLICATION_MODE"
})
def deploy(ctx, mode):
    """
    Updates the container cluster in development, acceptance or production environment on AWS to run a Docker image
    """
    target = "middleware"

    print(f"Starting deploy of {target}")

    print(f"Starting AWS session for: {mode}")
    session = boto3.Session(profile_name=ctx.config.aws.profile_name, region_name="eu-central-1")
    ecs_client = session.client('ecs')

    print("Deploying middleware:", ctx.config.env)
    ecs_client.update_service(
        cluster=FARGATE_CLUSTER_NAME,
        service="middleware",
        taskDefinition="middleware",
        forceNewDeployment=True,
    )

    print("Waiting for deploy to finish ...")
    await_steady_fargate_services(ecs_client, [target])
    print("Done deploying")
