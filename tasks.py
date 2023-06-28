from invoke import Collection

from environments.system_configuration.main import create_configuration_and_session
from commands.postgres.invoke import setup_postgres_localhost
from commands.deploy import prepare_builds, build, push, promote, deploy, migrate, print_available_images
from commands.aws.ecs import cleanup_ecs_artifacts
from commands.aws.repository import sync_repository_state


environment, _ = create_configuration_and_session()
container_collection = Collection("container", prepare_builds, build, push, promote, deploy)
database_collection = Collection("db", setup_postgres_localhost, migrate)
aws_collection = Collection("aws", print_available_images, sync_repository_state, cleanup_ecs_artifacts)
aws_collection.configure(environment)


namespace = Collection(
    container_collection,
    database_collection,
    aws_collection,
)
namespace.configure(environment)
