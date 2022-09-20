import argparse
import yaml
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import tqdm
import copy


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

total_docs = 0  ## count non-empty documents
def gen_doc(filepath, userid):
	global total_docs
	with open(filepath, 'r', encoding='utf-8') as fin:
		for line in fin:
			## remove empty lines
			if line.strip() != "":
				total_docs += 1
				yield {"message": line, "userid": userid}

def main(args):
	config = load_config(args.config)
	cfg_elastic = config['elastic']
	# Create the client instance
	client = Elasticsearch(
		cfg_elastic['host'],
		verify_certs=cfg_elastic['verify_certs'],
		ca_certs=cfg_elastic['certificate_path'],
		basic_auth=(cfg_elastic['username'], cfg_elastic['password'])
	)

	# Successful response!
	print(client.info())

	## get data info from config
	filepath = config['data']['filepath']
	userid = config['data']['userid']

	successes = 0
	progress = tqdm.tqdm(unit="docs")
	try:
		for success, info in streaming_bulk(
			client=client, actions=gen_doc(filepath, userid), index=cfg_elastic['index']):
			progress.update(1)
			successes += success
			if not success:
				print('A document failed:', info)
	except Exception as e:
		print(e)
	print(f"Indexed {successes}/{total_docs} documents")


	# doc = {
	# 	'message': '1662724635868	36	KeyEvent	KeyEvent://1/25		{\"keycodeString\":\"KEYCODE_VOLUME_DOWN\",\"package\":\"\",\"action\":1,\"source\":257,\"code\":25,\"eventTime\":2583640595,\"downTime\":2583640463}', 'userid': 'test_user_id'
	# }
	# resp = client.index(index="log_volume", document=doc)
	# print(resp)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Upload data to elasticsearch")
	parser.add_argument('-c', '--config', dest='config', action='store', default="config.yml", help="config YAML file")

	args = parser.parse_args()
	main(args)
