import argparse
from pprint import pprint

from AHKLogParser import AHKLogParser


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_file')

    return parser.parse_args()


def main(args):
    print("Parsing...")
    parser = AHKLogParser(args.log_file)

    filters = {
        "active": True,
        "duration": ["gt", 50]
    }

    pprint(["{} - {}".format(line.get_dict()["classification"], line.get_dict()["window_title"]) for line in parser.filter_by(filters)])

    print("{} lines in log file, {} distinct activities".format(len(parser.log_dict), len(parser.activity_log)))

if __name__ == '__main__':
    main(parse_args())
