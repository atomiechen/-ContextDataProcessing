FROM cschranz/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim
RUN mamba install --update-all --yes -c conda-forge jupyterlab && \
	mamba install --update-all --yes -c conda-forge jupyterlab-git && \
	mamba install --update-all --yes -c anaconda graphviz
