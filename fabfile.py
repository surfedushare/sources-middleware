from invoke import Collection

from environments.system_configuration.main import create_configuration_and_session
from commands.postgres.fabric import setup_postgres_remote
from commands.django import connect_with_shell


aws_collection = Collection("aws", connect_with_shell)
database_collection = Collection("db", setup_postgres_remote)


environment, _ = create_configuration_and_session()
namespace = Collection(
    aws_collection,
    database_collection
)
namespace.configure(environment)
