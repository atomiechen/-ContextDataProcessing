set -e

# start a temp container
docker run -it -d --name context-jupyter-tmp cschranz/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim

# start bash using root user in need of apt installing
docker exec -it --user root context-jupyter-tmp bash
# run commands in modifications.sh (one by one, retry on failure)

# stop container
docker stop context-jupyter-tmp
# commit container 
# if docker run using bash, then need to change CMD back: --change='CMD ["start-notebook.sh"]'
docker commit \
	-a "Atomie CHEN" \
	-m "from original gpu-jupyter: update conda, Jupyterlab; conda install jupyterlab-git, jupytext; allow showing hidden content; apt install graphviz, openssh-server; add conda to login PATH" \
	context-jupyter-tmp atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated2

# # delete tmp container if all done
# docker rm context-jupyter-tmp
