from invoke import Collection

from environments.system_configuration.main import create_configuration_and_session
from commands.postgres.fabric import setup_postgres_remote
from commands.django import connect_with_shell


environment, _ = create_configuration_and_session()
namespace = Collection(setup_postgres_remote, connect_with_shell)
namespace.configure(environment)
