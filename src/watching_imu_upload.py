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
            self.upload_dir = config['data']['upload_dir']
        except:
            self.upload_dir = "./unpacked_imu"

    def convertBin(self, path: str):
        new_dir = self.upload_dir + "/"
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        data_dir, data_filename = os.path.split(path)

        if data_filename.split(".")[-1] == "bin":
            with open(new_dir + data_filename.replace(".bin", ".txt"), "w", encoding='utf-8', errors='ignore') as f0:
                times = 0
                while True:
                    try:
                        f = open(os.path.join(data_dir, data_filename), 'rb')
                        break
                    except:
                        print(f"open times: {times}")
                        continue
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
                    f0.write(str(cur[0]))
                    for i in range(1, 4):
                        f0.write(", " + str(cur[i]))
                    f0.write(", " + str(int(cur[4])) + "\n")
                f.close()
            return new_dir + data_filename.replace(".bin", ".txt")
        elif data_filename.split(".")[-1] == "meta":
            with open(os.path.join(data_dir, data_filename), "r", encoding='utf-8', errors='ignore') as f:
                data_filename = data_filename.split(".")
                data_filename[-2] = "txt"
                data_filename = ".".join(data_filename)
                with open(new_dir + data_filename, "w", encoding='utf-8', errors='ignore') as f0:
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
    watching_path = config['data']['watching_dir']
    upload_path = config['data']['upload_dir']
    logger = init_logger('imu-upload-elastic', config['data']['log_dir'])
    with ThreadPoolExecutor() as executor:
        event_handler = IMUUploadHandler(config, executor, logger)
        event_handler.schedule_upload_folder(upload_path)
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