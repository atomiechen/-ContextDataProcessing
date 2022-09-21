import yaml
import copy
import os
import sys
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


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

## 新建文件夹
def mkdir(path):
	if not os.path.exists(path):
		os.makedirs(path, exist_ok=True)


## ref: https://stackoverflow.com/a/27865750/11854304
class Formatter(logging.Formatter):
	def __init__(self, *args, **kwargs):
		## use local timezone as default
		self.tz = kwargs.pop('tz', datetime.datetime.now().astimezone().tzinfo)
		super().__init__(*args, **kwargs)

	def converter(self, timestamp):
		return datetime.datetime.fromtimestamp(timestamp, tz=self.tz)

	def formatTime(self, record, datefmt=None):
		dt = self.converter(record.created)
		if datefmt:
			s = dt.strftime(datefmt)
		else:
			t = dt.strftime(self.default_time_format)
			s = self.default_msec_format % (t, record.msecs)
		return s


Beijing_timezone = datetime.timezone(datetime.timedelta(hours=8))
formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S.%f %z', tz=Beijing_timezone)

def init_logger(name: str, log_dirpath: str):
	mkdir(log_dirpath)

	## rollover at midnight at Beijing time zone
	rollover_time = datetime.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=Beijing_timezone)

	## collect all logs to file
	normal_log_handler = TimedRotatingFileHandler(os.path.join(log_dirpath, "normal.log"), when="midnight", interval=1, atTime=rollover_time)
	normal_log_handler.setLevel(logging.DEBUG)
	normal_log_handler.setFormatter(formatter)
	normal_log_handler.suffix = "%Y%m%d_%H%M%S_%z"

	## collect error logs to file
	error_log_handler = TimedRotatingFileHandler(os.path.join(log_dirpath, "error.log"), when="midnight", interval=1, atTime=rollover_time)
	error_log_handler.setLevel(logging.ERROR)
	error_log_handler.setFormatter(formatter)
	error_log_handler.suffix = "%Y%m%d_%H%M%S_%z"

	## redirect all logs to console output
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.DEBUG)
	stdout_handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(normal_log_handler)
	logger.addHandler(error_log_handler)
	logger.addHandler(stdout_handler)

	return logger

def init_stdout_logger(name: str):
	## redirect all logs to console output
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.DEBUG)
	stdout_handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(stdout_handler)

	return logger
