from invoke import Collection

from environments.project import create_configuration_and_session
from commands.postgres.invoke import setup_postgres_localhost
from commands.deploy import (prepare_builds, build, push, deploy, migrate, print_available_images,
                             print_running_containers)


environment, _ = create_configuration_and_session(use_aws_default_profile=False)
aws_collection = Collection("aws", build, push, migrate, print_available_images, print_running_containers, deploy)
aws_collection.configure(environment)


namespace = Collection(
    aws_collection,
    prepare_builds,
    setup_postgres_localhost
)
namespace.configure(environment)
