import argparse
import yaml
from elasticsearch import Elasticsearch


def load_config(filename):
	with open(filename, 'r', encoding='utf-8') as fin:
		config = yaml.safe_load(fin)
	## 填充缺省值
	## 默认用户名为elastic
	if 'username' not in config:
		config['username'] = 'elastic'
	## 默认检查服务器证书
	if 'verify_certs' not in config:
		config['verify_certs'] = True
	## 默认证书地址为当前目录下的http_ca.crt
	if 'certificate_path' not in config:
		config['certificate_path'] = 'http_ca.crt'
	return config

def main(args):
	config = load_config(args.config)
	# Create the client instance
	client = Elasticsearch(
		config['host'],
		verify_certs=config['verify_certs'],
		ca_certs=config['certificate_path'],
		basic_auth=(config['username'], config['password'])
	)

	# Successful response!
	print(client.info())

	doc = {
		'message': '1662724635868	36	KeyEvent	KeyEvent://1/25		{\"keycodeString\":\"KEYCODE_VOLUME_DOWN\",\"package\":\"\",\"action\":1,\"source\":257,\"code\":25,\"eventTime\":2583640595,\"downTime\":2583640463}'
	}
	# resp = client.index(index="log_volume", document=doc)
	# print(resp)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Upload data to elasticsearch")
	# parser.add_argument('dirpath', action='store', help="Directory path")
	parser.add_argument('-c', '--config', dest='config', action='store', default="config.yml", help="config YAML file")

	args = parser.parse_args()
	main(args)
