from invoke import Collection

from environments.project import create_configuration_and_session
from commands.postgres.fabric import setup_postgres_remote
from commands.django import connect_with_shell


environment, _ = create_configuration_and_session(use_aws_default_profile=False)
namespace = Collection(setup_postgres_remote, connect_with_shell)
namespace.configure(environment)
