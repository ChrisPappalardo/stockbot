FROM quantopian/zipline
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV TERM xterm

# update, upgrade, and install packages
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y apt-utils \
    && apt-get install -y nano less make \
    && apt-get install -y python-dev python3-dev

# configure apt-utils (fixes warnings)
RUN dpkg-reconfigure apt-utils

# install requirements, package, and tox
COPY . /app
RUN pip install -r /app/requirements/base.txt
RUN pip install /app
RUN pip install tox

# stage the entrypoint
COPY ./compose/stockbot/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
