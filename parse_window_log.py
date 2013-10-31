import argparse
from pprint import pprint

from AHKLogParser import AHKLogParser

"""
    Graph ideas:
        Time spent in each category
        Time spent in categories over time
        Most popular programs
        Idle vs active periods
        Wordle graphic from words in window titles
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_file')

    return parser.parse_args()


def main(args):
    # print("Parsing...")
    parser = AHKLogParser(args.log_file)

    filters = {
        "active": True,
        # "classification": ["any", ["other"]]
    }

    # filtered_data = [activity for activity in parser.filter_by(filters)]

    # pprint(filtered_data)

    # print("{} activity found, {} lines in log file, {} distinct activities".format(len(filtered_data), len(parser.log_dict), len(parser.activity_log)))

    # for activity in filtered_data:
    #     print ("{} - {}".format(activity["classification"][0], activity["window_title"]))

    print_csv_count("classification", parser, filters)
    

def print_csv_count(count_property, parser, filters={}):
    print("Category, Time Spent")
    for category, count in parser.count_by(count_property, filters).iteritems():
        print("{}, {}".format(category, count))


if __name__ == '__main__':
    main(parse_args())
