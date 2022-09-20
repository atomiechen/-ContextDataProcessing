import argparse
import yaml
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import tqdm


def load_config(filepath):
	with open(filepath, 'r', encoding='utf-8') as fin:
		config = yaml.safe_load(fin)
	## 填充缺省值
	if 'elastic' not in config:
		config['elastic'] = {}
	cfg_elastic = config['elastic']
	## 默认用户名为elastic
	if 'username' not in cfg_elastic:
		cfg_elastic['username'] = 'elastic'
	## 默认检查服务器证书
	if 'verify_certs' not in cfg_elastic:
		cfg_elastic['verify_certs'] = True
	## 默认证书地址为当前目录下的http_ca.crt
	if 'certificate_path' not in cfg_elastic:
		cfg_elastic['certificate_path'] = 'http_ca.crt'
	return config

## ref: https://stackoverflow.com/a/27518377/11854304
def count_lines(filepath):
	def _make_gen(reader):
		b = reader(1024 * 1024)
		while b:
			yield b
			b = reader(1024*1024)
	with open(filepath, 'rb') as f:
		f_gen = _make_gen(f.raw.read)
		return sum( buf.count(b'\n') for buf in f_gen )

def gen_doc(filepath, userid):
	with open(filepath, 'r', encoding='utf-8') as fin:
		for line in fin:
			## remove empty lines
			if line.strip() != "":
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

	number_of_docs = count_lines(filepath)
	successes = 0
	progress = tqdm.tqdm(unit="docs", total=number_of_docs)
	for success, info in streaming_bulk(
		client=client, actions=gen_doc(filepath, userid), index='log_volume'):
		progress.update(1)
		successes += success
		if not success:
			print('A document failed:', info)
	
	print(f"Indexed {successes}/{number_of_docs} documents")


	# doc = {
	# 	'message': '1662724635868	36	KeyEvent	KeyEvent://1/25		{\"keycodeString\":\"KEYCODE_VOLUME_DOWN\",\"package\":\"\",\"action\":1,\"source\":257,\"code\":25,\"eventTime\":2583640595,\"downTime\":2583640463}'
	# }
	# resp = client.index(index="log_volume", document=doc)
	# print(resp)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Upload data to elasticsearch")
	# parser.add_argument('dirpath', action='store', help="Directory path")
	parser.add_argument('-c', '--config', dest='config', action='store', default="config.yml", help="config YAML file")

	args = parser.parse_args()
	main(args)
