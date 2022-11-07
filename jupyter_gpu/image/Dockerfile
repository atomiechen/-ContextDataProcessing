FROM cschranz/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim
# RUN mamba install --update-all --yes -c conda-forge jupyterlab && \
# 	mamba install --update-all --yes -c conda-forge jupyterlab-git && \
# 	mamba install --update-all --yes -c anaconda graphviz

# use BuildKit features to cache downloaded conda packages: https://docs.docker.com/build/buildkit
RUN --mount=type=cache,target=/opt/conda/pkgs \
	conda update --yes -n base conda && \
	conda update --yes -c conda-forge jupyterlab && \
	conda install --yes -c conda-forge jupyterlab-git && \
	conda install --yes -c conda-forge jupytext && \
	conda install --yes -c anaconda graphviz && \
	conda clean -all --yes --verbose && \
	echo -e "\nc.ContentsManager.allow_hidden = True" >> etc/jupyter/jupyter_server_config.py
