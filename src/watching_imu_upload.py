import os
import json
import struct
from watching_upload import UploadHandler
import argparse
from logging import Logger
import time
from concurrent.futures import Executor, Future, ThreadPoolExecutor
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from elastic_upload import ElasticUploader
from utils import load_config, init_logger, init_stdout_logger

class IMUUploadHandler(UploadHandler):
    def __init__(self, config: dict, executor: Executor, logger: Logger = None):
        super().__init__(config, executor, logger)

        try:
            self.upload_imu_dir = config['data']['upload_imu_dir']
            self.uploaded_imu_list_path = config['data']['uploaded_imu_list_path']
            with open(self.uploaded_imu_list_path, 'r', encoding='utf-8') as fin:
                self.uploaded_imu_set = set(line.strip() for line in fin)
        except:
            self.uploaded_imu_list_path = "_uploaded_imu_list.txt"
            self.uploaded_imu_set = set()

    def convertBin(self, path: str):
        new_dir = self.upload_imu_dir + "/"
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        data_dir = path.split("/")
        data_filename = data_dir[-1]
        data_dir[-1] = ""
        data_dir = "/".join(data_dir)
        filenames = os.listdir(data_dir)

        if data_filename.split(".")[-1] == "bin":
            reason_filename = data_filename + ".meta"
            if reason_filename in filenames:
                with open(os.path.join(data_dir, reason_filename), "r") as f:
                    commits = json.loads(f.readline())
                    reason = commits["commit"].split("\n")[-1]
                with open(new_dir + data_filename.replace(".bin", ".txt"), "w") as f0:
                    f = open(os.path.join(data_dir, data_filename), 'rb')
                    flag = True
                    while flag:
                        cur = []
                        for i in range(4):
                            tmp = f.read(4)
                            if len(tmp) < 4:
                                flag = False
                                break
                            cur.append(struct.unpack('>f', tmp)[0])
                        tmp = f.read(8)
                        if len(tmp) < 8:
                            flag = False
                            continue
                        cur.append(struct.unpack('>d', tmp)[0])
                        if len(cur) < 5:
                            continue
                        f0.write(json.dumps(cur))
                        f0.write("\n")
                    f.close()
            return new_dir + data_filename.replace(".bin", ".txt")
        elif data_filename.split(".")[-1] == "meta":
            with open(os.path.join(data_dir, data_filename), "r") as f:
                with open(new_dir + data_filename, "w") as f0:
                    f0.writelines(f.readlines())
            return new_dir + data_filename

    def on_any_event(self, event: FileSystemEvent):
        self.logger.info(f'Event: {event.event_type} Path: {event.src_path}')
        if event.event_type == 'created':
            ### 受到新建文件事件后，总是重新上传以更新文档，因此force_upload=True
            if event.src_path.split(".")[-1] in ["bin", "meta"]:
                to_upload_path = self.convertBin(event.src_path)
                ft = self.executor.submit(self.check_and_upload, to_upload_path, True)

def main(args):
	config = load_config(args.config)
	watching_path = config['data']['watching_imu_dir']
	logger = init_logger('imu-upload-elastic', config['data']['log_imu_dir'])
	with ThreadPoolExecutor() as executor:
		event_handler = IMUUploadHandler(config, executor, logger)
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