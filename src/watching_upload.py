import argparse
import os
import time
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from elastic_upload import ElasticUploader
from utils import load_config, Beijing_timezone


class MyHandler(FileSystemEventHandler):
	def __init__(self, config):
		super().__init__()
		self.uploader = ElasticUploader(config)

	def on_any_event(self, event):
		print(f'{datetime.now(tz=Beijing_timezone)}  Event: {event.event_type}  Path: {event.src_path}')
		if event.event_type == 'created':
			abs_path = os.path.abspath(event.src_path)
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
						self.uploader.upload(abs_path, userid)
						print(f"Uploaded: {abs_path}")
					except Exception:
						pass


def main(args):
	config = load_config(args.config)
	watching_path = config['data']['watching_dir']
	event_handler = MyHandler(config)
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
