from invoke.tasks import task

from commands.aws.ecs import run_data_engineering_task


@task(help={
    "mode": "Mode you want to migrate: development, acceptance or production. Must match APPLICATION_MODE"
})
def migrate(ctx, mode):
    """
    Executes migration task on container cluster for development, acceptance or production environment on AWS
    """
    command = ["python", "manage.py", "migrate"]
    environment = [
        {
            "name": "DET_POSTGRES_USER",
            "value": f"{ctx.config.postgres.user}"
        },
        {
            "name": "DET_SECRETS_POSTGRES_PASSWORD",
            "value": f"{ctx.config.aws.postgres_password_arn}"
        },
    ]
    run_data_engineering_task(ctx, mode, command, environment)
