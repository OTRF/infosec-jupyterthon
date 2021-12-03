# Infosec Jupyterthon script: Jupyter Environment Dockerfile
# Author: Ashwin Patil @ashwinpatil & Roberto Rodriguez @Cyb3rWard0g
# License: GPL-3.0

ARG BASE_CONTAINER=jupyter/pyspark-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Ashwin Patil @ashwinpatil & Roberto Rodriguez @Cyb3rWard0g"
LABEL description="Dockerfile Infosec Jupyterthon Project."

ARG YEAR="2021"

USER root

# R pre-requisites
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    fonts-dejavu \
    unixodbc \
    unixodbc-dev \
    r-cran-rodbc \
    gfortran \
    gcc \
    python3-gi \
    python3-gi-cairo \
    gir1.2-secret-1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# R packages including IRKernel which gets installed globally.
# r-e1071: dependency of the caret R package
RUN mamba install --quiet --yes \
    'r-base' \
    'r-caret' \
    'r-crayon' \
    'r-devtools' \
    'r-e1071' \
    'r-forecast' \
    'r-hexbin' \
    'r-htmltools' \
    'r-htmlwidgets' \
    'r-irkernel' \
    'r-nycflights13' \
    'r-randomforest' \
    'r-rcurl' \
    'r-rodbc' \
    'r-rsqlite' \
    'r-shiny' \
    'unixodbc' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# These packages are not easy to install under arm
# hadolint ignore=SC2039
RUN set -x && \
    arch=$(uname -m) && \
    if [ "${arch}" == "x86_64" ]; then \
        mamba install --quiet --yes \
            'r-rmarkdown' \
            'r-tidymodels' \
            'r-tidyverse' && \
            mamba clean --all -f -y && \
            fix-permissions "${CONDA_DIR}" && \
            fix-permissions "/home/${NB_USER}"; \
    fi;

# Add conda to path
ENV PATH /opt/conda/envs/env/bin:$PATH
# Environment variable for Pip and conda packages to be installed
ENV INSTALL_CONDA_PACKAGES jupyter_contrib_nbextensions jupyterthemes selenium phantomjs autopep8 plotly qgrid black pandas-profiling rise vega vega_datasets
ENV INSTALL_PIP_PACKAGES azure-cli jupyterlab-git pyvis setuptools_git pandas-bokeh nbcommands awscli attackcti splunk-sdk elasticsearch elasticsearch-dsl geoip2 untangle huntlib requests requests-html graphistry openhunt==1.6.6 jupyter_bokeh wordcloud
ENV INSTALL_MSTICPY_DEV_PACKAGES aiohttp>=3.0.0 bandit>=1.7.0 beautifulsoup4 black>=20.8b1 coverage>=5.5 filelock>=3.0.0 flake8>=3.8.4 markdown>=3.3.4 mccabe>=0.6.1 mypy>=0.812 nbdime>=2.1.0 pep8-naming>=0.10.0 pep8>=1.7.1 pipreqs>=0.4.9 prospector>=1.3.1 pycodestyle>=2.6.0 pydocstyle>=6.0.0 pyflakes>=2.2.0 pylint>=2.5.3 pyroma>=3.1 pytest-check>=1.0.1 pytest-cov>=2.11.1 pytest>=5.0.1 responses>=0.13.2 sphinx>=2.1.2 sphinx_rtd_theme>=0.5.1 virtualenv 
# Install conda and pip packages 
RUN conda install --quiet --yes ${INSTALL_CONDA_PACKAGES} && \
pip install llvmlite --ignore-installed && \
pip install --upgrade --quiet ${INSTALL_PIP_PACKAGES} && \
pip install --upgrade --quiet ${INSTALL_MSTICPY_DEV_PACKAGES} && \
mkdir /home/$NB_USER/.msticpy && \
conda clean --all -f -y && \
rm -rf "/home/${NB_USER}/.cache/yarn" && \
# Clone msticpy and other github directories with sample notebooks
git clone https://github.com/microsoft/msticpy.git && \
pip install -e /home/$NB_USER/msticpy && \
git clone https://github.com/microsoft/msticnb.git && \
pip install -e /home/$NB_USER/msticnb

# Activate ipywidgets extension in the environment that runs the notebook server
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    jupyter nbextension enable toc2/main --sys-prefix && \
    jupyter nbextension enable execute_time/ExecuteTime --sys-prefix && \
    jupyter nbextension enable python-markdown/main --sys-prefix && \
    jupyter nbextension enable codefolding/main --sys-prefix && \
    jupyter nbextension enable autosavetime/main --sys-prefix && \
    jupyter nbextension enable tree-filter/index --sys-prefix && \
    jupyter nbextension enable hide_input_all/main --sys-prefix && \
    jupyter nbextension enable hinterland/hinterland --sys-prefix && \
    jupyter nbextension enable varInspector/main --sys-prefix && \
    jupyter nbextension enable spellchecker/main --sys-prefix && \
    jupyter nbextension enable toggle_all_line_numbers/main --sys-prefix && \
    jupyter nbextension enable --py qgrid --sys-prefix && \
    jupyter nbextension install https://github.com/drillan/jupyter-black/archive/master.zip --sys-prefix && \
    jupyter nbextension install --py nbdime --sys-prefix && \
    jupyter nbextension enable jupyter-black-master/jupyter-black --sys-prefix && \
    jupyter nbextension enable nbdime --py --sys-prefix && \
    jupyter nbextension enable rise --py --sys-prefix && \
    jupyter nbextensions_configurator enable --sys-prefix && \
    jupyter labextension install @jupyterlab/git --no-build && \
    jupyter labextension install @jupyterlab/github --no-build && \
    jupyter labextension enable git && \
    jupyter lab build --dev-build=False

COPY docs/2020/notebooks ${HOME}/docs/2020/notebooks
COPY docs/${YEAR}/sessions ${HOME}/docs/${YEAR}/sessions
COPY docs/workshops ${HOME}/docs/workshops

USER root
RUN fix-permissions ${HOME}/docs

USER ${NB_UID}

WORKDIR "${HOME}"
