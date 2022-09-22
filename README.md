# 情境数据处理



## 监听上传

`src/watching_upload.py`：监听文件夹，将内部文件上传并实时上传新建的文件

- 指定`-c config.yml`来读取程序设置

使用Docker运行：首先修改`docker-compose.yml`里挂载的数据路径，然后在`src/config.yml`里配置要监听的数据文件夹，最后在根目录运行

```sh
docker-compose up -d
```



## Docker运行Elasticsearch和Kibana

### 命令行启动（方便测试）

参考：

- https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
- https://www.elastic.co/guide/en/kibana/current/docker.html



```sh
# 建立网络
docker network create elastic

# 启动elasticsearch，注意配置端口和内存设置；命令行中会显示token和密码，需要存下来
docker run --name es-node01 --net elastic -p 19213:9200 -p 19313:9300 -e "ES_JAVA_OPTS=-Xms4g -Xmx4g" -t docker.elastic.co/elasticsearch/elasticsearch:8.4.1

# 启动kibana，然后在浏览器中进行配置
docker run --name kib-01 --net elastic -p 15613:5601 docker.elastic.co/kibana/kibana:8.4.1

# 使用完毕后，删除两个container和新建的网络
docker rm es-node01
docker rm kib-01
docker network rm elastic
```



### docker compose启动（推荐）

使用docker-compose.yml配置文件启动，注意elasticsearch不会在命令行显示token和密码，需要通过elasticsearch/bin/elasticsearch-reset-password来重置密码

进入`elastic_kibana`文件夹，运行

```sh
docker-compose up -d
```



### 重置密码和token

重置token：

```sh
docker exec -it <elasticsearch容器名> /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

重置密码：

```sh
docker exec -it <elasticsearch容器名> /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

如果输入token后kibana需要验证码：

```sh
docker exec -it <kibana容器名> /usr/share/kibana/bin/kibana-verification-code
```


