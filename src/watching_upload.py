import argparse
from logging import Logger
import os
import time
import json
from concurrent.futures import Executor, Future, ThreadPoolExecutor
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from elastic_upload import ElasticUploader
from utils import load_config, init_logger, init_stdout_logger


class UploadHandler(FileSystemEventHandler):
	def __init__(self, config: dict, executor: Executor, logger: Logger = None):
		super().__init__()
		if logger:
			self.logger = logger
		else:
			self.logger = init_stdout_logger("UploadHandler")
		self.uploader = ElasticUploader(config, self.logger)
		self.executor = executor
		self.set_lock = threading.Lock()
		
		## read in uploaded file list
		try:
			self.uploaded_list_path = config['data']['uploaded_list_path']
			with open(self.uploaded_list_path, 'r', encoding='utf-8') as fin:
				self.uploaded_set = set(line.strip() for line in fin)
				fin.close()
		except:
			self.uploaded_list_path = "_uploaded_list.txt"
			self.uploaded_set = set()


	def on_any_event(self, event: FileSystemEvent):
		self.logger.info(f'Event: {event.event_type} Path: {event.src_path}')
		if event.event_type == 'created':
			### 受到新建文件事件后，总是重新上传以更新文档，因此force_upload=True
			ft = self.executor.submit(self.check_and_upload, event.src_path, True)

	def check_and_upload(self, path: str, force_upload=False):
		abs_path = os.path.abspath(path)
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
			
			## (no forcing upload) if already uploaded, skip it
			if not force_upload and abs_path in self.uploaded_set:
				return

			## valid file and need to upload
			if need_upload:
				## get user ID from meta file
				try:
					with open(meta_path, 'r', encoding='utf-8') as fin:
						data = json.load(fin)
						fin.close()
					userid = data['userId']
					if self.uploader.upload(abs_path, userid):
						## record this uploaded file
						with self.set_lock:
							self.uploaded_set.add(abs_path)
							self.write_uploaded_list()
						self.logger.info(f"Uploaded: {abs_path}")
					else:
						self.logger.error(f"Failed to upload: {abs_path}")
				except Exception as e:
					self.logger.exception(f"Failed to upload: {abs_path}, with exception: {e}")

	def write_uploaded_list(self):
		with open(self.uploaded_list_path, 'w', encoding='utf-8') as fout:
			for item in self.uploaded_set:
				fout.write(item + "\n")
			fout.close()

	def schedule_upload_folder(self, dirpath):
		self.logger.info(f"Start uploading folder: {dirpath}")
		return self.executor.submit(self.traverse_folder, dirpath).add_done_callback(
			lambda ft: self.upload_folder_callback(ft, dirpath)
			)
	
	def upload_folder_callback(self, future: Future, dirpath):
		try:
			future.result()
			self.logger.info(f"Folder uploaded: {dirpath}")
		except Exception as e:
			self.logger.exception(f"Failed to upload folder: {dirpath}, Exception: {e}")

	def traverse_folder(self, dirpath):
		if not os.path.isdir(dirpath):
			return
		for item in os.listdir(dirpath):
			full_path = os.path.join(dirpath, item)
			if os.path.isdir(full_path):
				self.traverse_folder(full_path)
			else:
				self.check_and_upload(full_path)


def main(args):
	config = load_config(args.config)
	watching_path = config['data']['watching_dir']
	logger = init_logger('context-upload-elastic', config['data']['log_dir'])
	with ThreadPoolExecutor() as executor:
		event_handler = UploadHandler(config, executor, logger)
		event_handler.schedule_upload_folder(watching_path)
		observer = Observer()
		observer.schedule(event_handler, watching_path, recursive=True)
		observer.start()
		logger.info(f"Watching events for folder: {watching_path}")
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
