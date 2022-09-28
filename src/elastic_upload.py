import argparse
from logging import Logger
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

from utils import load_config, init_stdout_logger


class ElasticUploader:
	def __init__(self, config: dict, logger: Logger = None):
		self.config = config['elastic']
		self.total_docs = 0
		# Create the client instance
		self.client = Elasticsearch(
			self.config['host'],
			verify_certs=self.config['verify_certs'],
			ca_certs=self.config['certificate_path'],
			basic_auth=(self.config['username'], self.config['password'])
		)
		if logger:
			self.logger = logger
		else:
			self.logger = init_stdout_logger("ElasticUploader")
		# Successful response!
			self.logger.info(self.client.info())

	def gen_doc(self, filepath: str, userid: str):
		with open(filepath, 'r', encoding='utf-8') as fin:
			for line in fin:
				## remove empty lines
				if line.strip() != "":
					yield {"message": line, "userid": userid}
			fin.close()

	def upload(self, filepath: str, userid: str):
		total_docs = -1
		successes = 0
		## count non-empty documents
		try:
			with open(filepath, 'r', encoding='utf-8') as fin:
				total_docs = sum(1 for line in fin if line.strip())
				fin.close()
			for success, info in streaming_bulk(
				client=self.client, actions=self.gen_doc(filepath, userid), index=self.config['index']):
				successes += success
				if not success:
					self.logger.info('A document failed:', info)
		except Exception as e:
			self.logger.exception(e)
		self.logger.info(f"Indexed {successes}/{total_docs} documents")
		return total_docs == successes


def main(args):
	config = load_config(args.config)
	uploader = ElasticUploader(config)
	## get data info from config
	filepath = config['data']['filepath']
	userid = config['data']['userid']
	uploader.upload(filepath, userid)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Upload data to elasticsearch")
	parser.add_argument('-c', '--config', dest='config', action='store', default="config.yml", help="config YAML file")

	args = parser.parse_args()
	main(args)
