# Infosec Jupyterthon script: Jupyter Environment Dockerfile
# Author: Roberto Rodriguez (@Cyb3rWard0g)
# License: GPL-3.0

FROM cyb3rward0g/jupyter-pyspark:0.0.4
LABEL maintainer="Roberto Rodriguez @Cyb3rWard0g"
LABEL description="Dockerfile Infosec Jupyterthon Project."

ARG NB_USER
ARG NB_UID
ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}
ENV PATH "$HOME/.local/bin:$PATH"

USER root

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER} \
    && chown -R ${NB_USER}:${NB_USER} ${HOME} ${JUPYTER_DIR}

USER ${NB_USER}

RUN python3 -m pip install \
    openhunt==1.6.6 RISE==5.6.1 emoji==0.5.4 msticpy statsmodels==0.11.1 pyvis==0.1.7.0 --user

COPY docs ${HOME}/docs

USER root

RUN chown -R ${NB_USER}:${NB_USER} ${HOME} ${JUPYTER_DIR}

WORKDIR ${HOME}

USER ${NB_USER}