# source image
FROM atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated as initial

# dest image
FROM scratch
COPY --from=initial / /

ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

USER root
ENV DEBIAN_FRONTEND noninteractive

# Configure environment
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    NB_USER="${NB_USER}" \
    NB_UID=${NB_UID} \
    NB_GID=${NB_GID} \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH="${CONDA_DIR}/bin:${PATH}" \
    HOME="/home/${NB_USER}"

EXPOSE 8888

# Configure container startup
ENTRYPOINT ["tini", "-g", "--"]
CMD ["start-notebook.sh"]

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

WORKDIR "${HOME}"
