docker stop context-jupyter
docker rm context-jupyter
# docker run --gpus all -d -it --name context-jupyter --restart always -p 29503:8888 -v $(pwd)/data:/home/jovyan/work -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes -e NOTEBOOK_ARGS="--collaborative" --user root cschranz/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim
# docker run --gpus all -d -it --name context-jupyter --restart always -p 29503:8888 -v $(pwd)/data:/home/jovyan/work -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes -e NOTEBOOK_ARGS="--collaborative" atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated

# set user password (note those single quotes), start ssh service and Jupyter Lab
docker run -d -it \
	--name context-jupyter \
	--gpus all \
	--restart always \
	-p 29503:8888 \
	-p 29505:22 \
	-v $(pwd)/data:/home/jovyan/work \
	-e GRANT_SUDO=yes \
	-e JUPYTER_ENABLE_LAB=yes \
	-e NOTEBOOK_ARGS="--collaborative" \
	--user root \
	atomie/gpu-jupyter:squash \
	bash -c "echo '$(cat user_pass.txt)' | chpasswd --encrypted && service ssh start && start-notebook.sh"
	# atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated
