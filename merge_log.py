import argparse
import os
from datetime import datetime
from tqdm import tqdm


USER_LOG_FMT = "merged_{}.log"

def write_log_file(filename, fout):
	with open(filename, 'r', encoding='utf-8') as fin:
		for line in fin:
			if line.strip() != "":
				fout.write(line)

def traverseRootFolder(dirpath, output_dirpath):
	if not os.path.isdir(dirpath) or not os.path.isdir(output_dirpath):
		return
	for user in os.listdir(dirpath):
		traverseUserFolder(os.path.join(dirpath, user), output_dirpath)

def traverseUserFolder(dirpath, output_dirpath):
	if not os.path.isdir(dirpath) or not os.path.isdir(output_dirpath):
		return
	folder_list = []
	for item in os.listdir(dirpath):
		if os.path.isdir(os.path.join(dirpath, item)):
			try:
				## parse to check validity
				date_object = datetime.strptime(item, "%Y-%m-%d")
				# print(date_object)
				folder_list.append(item)
			except:
				pass
	if len(folder_list) > 0:
		folder_list.sort()
		user = os.path.split(dirpath)[-1]
		print(f"Merging user folder: {user}")
		print(folder_list)
		output_filepath = os.path.join(output_dirpath, USER_LOG_FMT.format(user))
		with open(output_filepath, 'w', encoding='utf-8') as fout:
			for item in tqdm(folder_list):
				traverseDateFolder(os.path.join(dirpath, item), fout)

def traverseDateFolder(dirpath, fout):
	if not os.path.isdir(dirpath):
		return
	file_list = []
	all_files = os.listdir(dirpath)
	for item in all_files:
		## check if valid log file
		if os.path.isfile(os.path.join(dirpath, item)) and item + ".meta" in all_files:
			file_list.append(item)
	file_list.sort()
	for filename in file_list:
		write_log_file(os.path.join(dirpath, filename), fout)

def main(args):
	dirpath = args.dirpath
	output_dirpath = args.output
	if args.user:
		traverseUserFolder(dirpath, output_dirpath)
	else:
		traverseRootFolder(dirpath, output_dirpath)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('dirpath', action='store', help="Directory path")
	parser.add_argument('-u', dest='user', action='store_true', default=False, help="start from user folder")
	parser.add_argument('-o', dest='output', action='store', default=".", help="output directory path")

	args = parser.parse_args()
	main(args)
