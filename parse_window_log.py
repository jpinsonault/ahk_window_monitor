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
        "is_classified": False
    }

    filtered_data = ["{} - {}".format(activity["classification"], activity["window_title"]) for activity in parser.filter_by(filters)]

    pprint(filtered_data)

    print("{} activity found, {} lines in log file, {} distinct activities".format(len(filtered_data), len(parser.log_dict), len(parser.activity_log)))

if __name__ == '__main__':
    main(parse_args())
