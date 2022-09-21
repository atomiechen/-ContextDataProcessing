FROM python:3.8
VOLUME /data
VOLUME /src
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /src
CMD ["python", "watching_upload.py"]
