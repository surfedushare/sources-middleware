from invoke.tasks import task

from commands.aws.ecs import run_task


@task(help={
    "mode": "Mode you want to migrate: development, acceptance or production. Must match APPLICATION_MODE",
    "version": "Version of the project you want to migrate. Defaults to latest version"
})
def migrate(ctx, mode, version=None):
    """
    Executes migration task on container cluster for development, acceptance or production environment on AWS
    """
    command = ["python", "manage.py", "migrate"]
    environment = [
        {
            "name": "INVOKE_POSTGRES_USER",
            "value": f"{ctx.config.postgres.user}"
        },
        {
            "name": "INVOKE_SECRETS_POSTGRES_PASSWORD",
            "value": f"{ctx.config.aws.postgres_password_arn}"
        },
    ]
    run_task(ctx, mode, command, environment, version=version)
