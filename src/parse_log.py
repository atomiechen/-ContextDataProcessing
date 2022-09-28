import argparse
import os
from datetime import datetime, timezone, timedelta

beijingTimeZone = timezone(timedelta(hours=8))

def parse_line(line):
	paras = line.strip().split('\t')
	timestamp = int(paras[0])
	date_object = datetime.fromtimestamp(timestamp/1000, tz=beijingTimeZone)
	return date_object.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def parse_log(filepath):
	head, tail = os.path.split(filepath)
	out_filepath = os.path.join(head, "parsed_" + tail)
	print(f'Reading from {filepath}')
	print(f'Writing to {out_filepath}')
	with open(filepath, 'r', encoding='utf-8') as fin:
		with open(out_filepath, 'w', encoding='utf-8') as fout:
			for line in fin:
				date_str = parse_line(line)
				fout.write(date_str + '\t' + line)

def main(args):
	for filepath in args.filepath:
		parse_log(filepath)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Append datetime to log file")
	parser.add_argument('filepath', nargs='+', action='store', help="Input file path; can have multiple paths")
	args = parser.parse_args()
	main(args)
