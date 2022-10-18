# Elasticsearch & Kibana 配置

## Docker运行

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

使用前，如果需要让elasticsearch的数据和logs文件夹从外部挂载（将数据保存在容器之外），需要保证挂载的文件夹能够被elasticsearch用户通过uid:gid `1000:0`访问。可使用如下方法（参考：https://www.elastic.co/guide/en/elasticsearch/reference/8.4/docker.html#_configuration_files_must_be_readable_by_the_elasticsearch_user）：

```sh
mkdir esdatadir
chmod g+rwx esdatadir
chgrp 0 esdatadir
```

然后在启动elasticsearch容器时配置环境变量`path.data`和`path.logs`分别为对应的路径（已经在docker-compose.yml中写好，也可以直接覆盖elasticsearch.yml中的配置项），参考：https://www.elastic.co/guide/en/elasticsearch/reference/8.4/important-settings.html#path-settings。

使用docker-compose.yml配置文件启动elasticsearch和kibana容器，注意elasticsearch不会在命令行显示token和密码，需要通过elasticsearch/bin/elasticsearch-reset-password来重置密码

```sh
docker-compose up -d
```



### 重置密码和token

假设elasticsearch容器名为context-elasticsearch，kibana容器名为context-kibana

重置token：

```sh
docker exec -it context-elasticsearch /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

重置密码：

```sh
docker exec -it context-elasticsearch /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

如果输入token后kibana需要验证码：

```sh
docker exec -it context-kibana /usr/share/kibana/bin/kibana-verification-code
```



## 运行后数据准备配置

### 设置Ingest Pipeline

主要步骤：

- 将输入字符串message解析为单独的域
- 根据部分field设置唯一文档ID
- 将timestamp解析为日期格式的@timestamp域
- 将evt_logid域转换为long类型
- 删除timestamp域
- 将other域解析为json格式，解析出来的域放在根节点下
- 特判：behavior如果是布尔类型，转换为long类型

```json
PUT _ingest/pipeline/log_volume-pipeline
{
  "description": "Ingest pipeline created by text structure finder",
  "processors": [
    {
      "grok": {
        "field": "message",
        "patterns": [
          "%{POSINT:timestamp}\\t%{INT:evt_logid}\\t(?<evt_type>[^\\t]*)\\t(?<evt_action>[^\\t]*)\\t(?<evt_tag>[^\\t]*)\\t(%{GREEDYDATA:other})?"
        ]
      }
    },
    {
      "set": {
        "field": "_id",
        "value": "{{userid}}@{{timestamp}}@{{evt_logid}}@{{evt_type}}"
      }
    },
    {
      "date": {
        "field": "timestamp",
        "formats": [
          "UNIX_MS"
        ]
      }
    },
    {
      "convert": {
        "field": "timestamp",
        "type": "long",
        "ignore_missing": true
      }
    },
    {
      "convert": {
        "field": "evt_logid",
        "type": "long",
        "ignore_missing": true
      }
    },
    {
      "json": {
        "field": "other",
        "add_to_root": true,
        "ignore_failure": true
      }
    },
    {
      "remove": {
        "field": "other",
        "ignore_missing": true
      }
    },
    {
      "script": {
        "source": "if (ctx['behavior'] == false) {\n    ctx['behavior'] = 0;\n} else if (ctx['behavior'] == true) {\n   ctx['behavior'] = 1;\n}\n",
        "ignore_failure": true
      }
    }
  ]
}
```



### 设置Index

```
# 新建index
PUT /log_volume

# 设置index数据结构
PUT /log_volume/_mapping
{
  "properties": {
        "message": {
          "type": "text"
        },
        "userid": {
          "type": "keyword"
        },
        "@timestamp": {
          "type": "date"
        },
        "timestamp": {
          "type": "long"
        },
        "evt_logid": {
          "type": "long"
        },
        "evt_type": {
          "type": "keyword"
        },
        "evt_action": {
          "type": "keyword"
        },
        "evt_tag": {
          "type": "text"
        }
  }
}

# 设置pipeline
PUT /log_volume/_settings
{
  "index" : {
    "default_pipeline" : "log_volume-pipeline"
  }
}

# 查看设置
GET log_volume/_settings

# 查看index
GET log_volume

# 上传文档
POST /log_volume/_doc
{
  "message": """1663697633833	29	KeyEvent	KeyEvent://0/25		{"keycodeString":"KEYCODE_VOLUME_DOWN","package":"","action":0,"source":257,"code":25,"eventTime":2583639128,"downTime":2583639128}""",
  "userid": "test_cwh"
}

#### 以下命令仅供特殊情形使用 ####

# 删除文档
DELETE log_volume/_doc/EfByVYMBUWC9fmoG6y5X

# 删除所有document
POST /log_volume/_delete_by_query
{
  "query": { 
      "match_all": {}
  }
}
```



### 新建runtime field



runtime_vol_music

```
try {
	if (!doc['musicVolume'].empty) { 
        emit(doc['musicVolume'].value);
    } else if (!doc['systemVolume'].empty) { 
        emit(doc['systemVolume'].value);
    }
} catch (Exception e) {}
```

等价的scripted field（已不推荐使用）：

```
if (!doc['musicVolume'].empty) {
  return doc['musicVolume'].value 
} else if (!doc['systemVolume'].empty) { 
  return doc['systemVolume'].value 
} else { 
  return null
}
```



runtime_vol_music_percent

```
try {
    if (!doc['musicVolume'].empty) { 
        emit(100.0*doc['musicVolume'].value/doc['musicVolumeMax'].value);
    } else if (!doc['finalVolume'].empty) { 
        emit(doc['finalVolume'].value);
    }
} catch (Exception e) {}
```



runtime_app

```
try {
    if (!doc['app.keyword'].empty) {
        emit(doc['app.keyword'].value)
    } else if (!doc['new_app.keyword'].empty) {
        emit(doc['new_app.keyword'].value)
    }
} catch (Exception e) {}
```



经纬度字符串解析为Geo point

```
try {
    if (!doc['position_gps.keyword'].empty) {
        def split_coor = doc['position_gps.keyword'].value.splitOnToken(',');
        def lat = Double.parseDouble(split_coor[0]);
        def lon = Double.parseDouble(split_coor[1]);
        emit(lat,lon);
    } else if (!doc['now_position_gps.keyword'].empty) {
        def split_coor = doc['now_position_gps.keyword'].value.splitOnToken(',');
        def lat = Double.parseDouble(split_coor[0]);
        def lon = Double.parseDouble(split_coor[1]);
        emit(lat,lon);
    }
} catch (Exception e) {}
```



## 数据迁移

### Reindex迁移ES数据

参考：https://www.elastic.co/guide/en/elasticsearch/reference/8.4/docs-reindex.html#reindex-from-remote

需要在目标机的`elasticsearch.yml`或启动环境变量中配置如下选项的内容（更新需要重启），将源机的IP地址填入白名单：

```yaml
reindex.remote.whitelist: "otherhost:9200, another:9200, 127.0.10.*:9200, localhost:*"
```

解决证书问题：关闭SSL认证，在`elasticsearch.yml`里添加设置，参考：https://stackoverflow.com/a/73688880/11854304

```yaml
reindex.ssl.verification_mode: none
```

然后使用reindex API：

```
POST _reindex
{
  "source": {
    "remote": {
      "host": "https://otherhost:9200",
      "username": "elastic",
      "password": "pass"
    },
    "index": "log_volume"
  },
  "dest": {
    "index": "log_volume"
  }
}
```



### 迁移Kibana配置

直接将Kibana中的Saved Objects导出为ndjson文件，然后在新的Kibana中导入即可。
