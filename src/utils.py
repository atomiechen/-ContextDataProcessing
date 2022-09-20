import yaml
import copy

from datetime import datetime, timezone, timedelta

Beijing_timezone = timezone(timedelta(hours=8))

## 加载模板配置文件
TEMPLATE_PATH = "template_config.yml"
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as fin:
	BLANK = yaml.safe_load(fin)

## recursion, fill dict_target according to dict_default
def __recurse(dict_default, dict_target):
	for key in dict_default:
		if key in dict_target:
			if dict_target[key] is None:
				dict_target[key] = copy.deepcopy(dict_default[key])
			elif isinstance(dict_default[key], dict):
				__recurse(dict_default[key], dict_target[key])
		else:
			dict_target[key] = copy.deepcopy(dict_default[key])

## 加载配置文件，填充缺省值
def load_config(filepath):
	with open(filepath, 'r', encoding='utf-8') as fin:
		config = yaml.safe_load(fin)
	## 填充缺省值
	__recurse(BLANK, config)
	return config
