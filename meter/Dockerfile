# pull official base image
FROM python:3.7-alpine
#

# install dependencies
#RUN apk update && \
#    apk add --virtual build-deps gcc python-dev
RUN pip install --upgrade pip

# Our requirements are minimal, but it's good practice to install them
# first.  Put things that change less often towards the top of the
# Dockerfile.  Then if you need to rebuild the images, Docker will
# start running partway through the Dockerfile and skip over the steps
# where nothing's changed.
RUN pip install pika==1.2.0


# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# Actually install the application
WORKDIR /usr/src/app
# It's only a single file.  It has to be in the same directory as the
# Dockerfile, or a subdirectory, but not a parent or sibling.
#COPY publisher.py .
# When you just 'docker run publisher' with no command afterwards,
# default to this:
CMD ["python", "/usr/src/app/publisher.py"]

#
