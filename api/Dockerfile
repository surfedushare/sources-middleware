FROM python:3.12
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y less vim build-essential

# Create the app environment
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/static
RUN mkdir -p /usr/src/environments
WORKDIR /usr/src/app

# Adding an app user to prevent container access as root
# Most options speak for itself.
# The -r options make it a system user and group.
# The -m option forces a home folder (which Python tools rely upon rather heavily)
# We also add default Python user path to PATH so installed binaries get found
RUN groupadd -r app -g 1000 && useradd app -u 1000 -r -m -g app
ENV PATH="/home/app/.local/bin:${PATH}"
ENV PYTHONPATH="/usr/src/app"
# Give access to app user
RUN chown -R app:app /usr/src/app
RUN chown app:app /usr/src/static
RUN chown app:app /usr/src/environments

# Become app user to prevent attacks during install (possibly from hijacked PyPi packages)
USER app:app

# Python dependencies
COPY api/requirements.txt /usr/src/app/
RUN pip install -U --no-cache-dir --user pip
RUN pip install wheel
RUN pip install --no-cache-dir --user uwsgi==2.0.24
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application
COPY api /usr/src/app
# Copy environment configurations
# The default environment mode is production, but during image build we use the localhost mode
# This allows to run setup commands locally without loading secrets
COPY environments /usr/src/environments

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI if they don't exist
RUN export APPLICATION_MODE=localhost && export APPLICATION_CONTEXT=unprivileged && \
    python manage.py collectstatic --noinput

# Entrypoint sets our environment correctly
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8080 to allow communication to/from server
EXPOSE 8080
