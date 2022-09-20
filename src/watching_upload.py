import argparse
import os
import time
import json
from datetime import datetime
from concurrent.futures import Executor, ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from elastic_upload import ElasticUploader
from utils import load_config, Beijing_timezone


class UploadHandler(FileSystemEventHandler):
	def __init__(self, config: dict, executor: Executor):
		super().__init__()
		self.uploader = ElasticUploader(config)
		self.executor = executor
		
		## read in uploaded file list
		try:
			self.uploaded_list_path = config['data']['uploaded_list_path']
			with open(self.uploaded_list_path, 'r', encoding='utf-8') as fin:
				self.uploaded_set = set(line.strip() for line in fin)
		except:
			self.uploaded_list_path = "_uploaded_list.txt"
			self.uploaded_set = set()


	def on_any_event(self, event: FileSystemEvent):
		print(f'{datetime.now(tz=Beijing_timezone)}  Event: {event.event_type}  Path: {event.src_path}')
		if event.event_type == 'created':
			ft = self.executor.submit(self.check_and_upload, event.src_path)

	def check_and_upload(self, path: str):
		abs_path = os.path.abspath(path)
		### 受到新建文件事件后，总是重新上传以更新文档，因此注释下面这段代码
		# if abs_path in self.uploaded_set:
		# 	return
		if os.path.isfile(abs_path):
			tmp_add_meta = abs_path + ".meta"
			tmp_rm_meta = abs_path[:-5]
			need_upload = False
			## check if this file is data file
			if os.path.isfile(tmp_add_meta):
				meta_path = tmp_add_meta
				need_upload = True
			## check if this file is meta file
			elif abs_path[-5:] == ".meta" and os.path.isfile(tmp_rm_meta):
				meta_path = abs_path
				abs_path = tmp_rm_meta
				need_upload = True
			
			## valid file and need to upload
			if need_upload:
				## get user ID from meta file
				try:
					print(f"Try to upload {abs_path}")
					with open(meta_path, 'r', encoding='utf-8') as fin:
						data = json.load(fin)
					userid = data['userId']
					if self.uploader.upload(abs_path, userid):
						self.uploaded_set.add(abs_path)
						self.write_uploaded_list()
					print(f"Uploaded: {abs_path}")
				except:
					pass

	def write_uploaded_list(self):
		with open(self.uploaded_list_path, 'w', encoding='utf-8') as fout:
			for item in self.uploaded_set:
				fout.write(item + "\n")


def main(args):
	config = load_config(args.config)
	watching_path = config['data']['watching_dir']
	with ThreadPoolExecutor() as executor:
		event_handler = UploadHandler(config, executor)
		observer = Observer()
		observer.schedule(event_handler, watching_path, recursive=True)
		observer.start()
		print(f"Watching for path: {watching_path}")
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			observer.stop()
		observer.join()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Watching for file folder events and upload")
	parser.add_argument('-c', '--config', dest='config', action='store', default="config.yml", help="config YAML file")

	args = parser.parse_args()
	main(args)
