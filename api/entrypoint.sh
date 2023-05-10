#!/usr/bin/env bash


# Exit immediately on error
set -e


# Handles editable Python packages
# Convenient when having to update Datagrowth for this project
if [ "$APPLICATION_MODE" == "localhost" ]  && [ -d "/usr/src/datagrowth" ] && \
    [ $(pip show datagrowth | grep "Location:" | awk -F "/" '{print $NF}') == "site-packages" ]
then
    echo "Replacing datagrowth PyPi installation with editable version"
    pip uninstall -y datagrowth
    pip install -e /usr/src/datagrowth
fi

# Check for AWS credentials on localhost
# If the credentials are not available stop loading secrets to prevent errors
if [ "$APPLICATION_MODE" == "localhost" ] && [ ! -e "/home/app/.aws/credentials" ]; then
    echo "Not loading AWS secrets on localhost, because ~/.aws/credentials is missing. Errors may occur at runtime."
    export POL_AWS_LOAD_SECRETS=0
    unset AWS_PROFILE
fi


# Executing the normal commands
exec "$@"
