set -e

# start a temp container
docker run -it -d --name context-jupyter-tmp cschranz/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim bash

# do things here, retry on failure (or you can do following things in container's bash shell)
# allow showing hidden content
docker exec -it context-jupyter-tmp bash -c \
	"echo -e '\nc.ContentsManager.allow_hidden = True' >> /etc/jupyter/jupyter_server_config.py"
# update & install conda packages
docker exec -it context-jupyter-tmp conda update --yes -n base conda
docker exec -it context-jupyter-tmp conda update --yes -c conda-forge jupyterlab
docker exec -it context-jupyter-tmp conda install --yes -c conda-forge jupyterlab-git
docker exec -it context-jupyter-tmp conda install --yes -c conda-forge jupytext
docker exec -it context-jupyter-tmp conda install --yes -c anaconda graphviz
# clean all unused files
docker exec -it context-jupyter-tmp conda clean -all --yes --verbose

# stop container
docker stop context-jupyter-tmp
# commit container
docker commit \
	-a "Atomie CHEN" \
	-m "from original gpu-jupyter: update conda, Jupyterlab; install jupyterlab-git, jupytext, graphviz; allow showing hidden content" \
	context-jupyter-tmp atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated

# # delete tmp container if all done
# docker rm context-jupyter-tmp
