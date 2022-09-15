import argparse
import os
from tqdm import tqdm


USER_LOG_FMT = "merged_{}.log"

def mkdir(path):
	if not os.path.exists(path):
		os.makedirs(path, exist_ok=True)

def get_basename(path):
	path, tail = os.path.split(path)
	while tail == "":
		path, tail = os.path.split(path)
	return tail

def write_log_file(filename, fout):
	with open(filename, 'r', encoding='utf-8') as fin:
		for line in fin:
			if line.strip() != "":
				fout.write(line)

def merge_for_each_subfolder(dirpath, output_dirpath):
	if not os.path.isdir(dirpath):
		return
	for user in os.listdir(dirpath):
		merge_folder(os.path.join(dirpath, user), output_dirpath)

def merge_folder(dirpath, output_dirpath):
	if not os.path.isdir(dirpath):
		return
	file_list = []
	traverse_foler(dirpath, file_list)
	if len(file_list) > 0:
		file_list.sort()
		user = get_basename(dirpath)
		mkdir(output_dirpath)
		output_filepath = os.path.join(output_dirpath, USER_LOG_FMT.format(user))

		print(f"Merging folder: {user}")
		print(f"Output to: {output_filepath}")
		print(f"Need to merge {len(file_list)} log files")
		
		merge_logs(file_list, output_filepath)

def traverse_foler(dirpath, file_list):
	if not os.path.isdir(dirpath):
		return
	all_files = set(os.listdir(dirpath))
	for item in all_files:
		full_path = os.path.join(dirpath, item)
		if os.path.isdir(full_path):
			## check if folder
			traverse_foler(full_path, file_list)
		elif item + ".meta" in all_files:
			## check if valid log file
			file_list.append(full_path)

def merge_logs(file_list, output_filepath):
	with open(output_filepath, 'w', encoding='utf-8') as fout:
		for filename in tqdm(file_list):
			write_log_file(filename, fout)

def main(args):
	dirpath = args.dirpath
	output_dirpath = args.output
	if args.subfolder:
		merge_for_each_subfolder(dirpath, output_dirpath)
	else:
		merge_folder(dirpath, output_dirpath)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Merge log files")
	parser.add_argument('dirpath', action='store', help="Directory path")
	parser.add_argument('--sub', dest='subfolder', action='store_true', default=False, help="merge each subfolder to individual log file")
	parser.add_argument('-o', dest='output', action='store', default=".", help="output directory path")

	args = parser.parse_args()
	main(args)
