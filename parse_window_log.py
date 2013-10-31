import argparse
from pprint import pprint

from AHKLogParser import AHKLogParser

"""
    Graph ideas:
        Time spent in each category
        Most popular programs
        Time spent active, idle
        Time spent fullscreen
        Time spent on each monitor
        Wordle graphic from words in window titles
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_file')

    return parser.parse_args()


def main(args):
    parser = AHKLogParser(args.log_file)

    active_filter = {"active": True}
    browser_filter = {
        "active": True,
        "classification": ['all', ['browser']]
    }


    print_csv_count("classification", parser, active_filter)
    print_csv_count("classification", parser, browser_filter)
    print_csv_count("active", parser)
    print_csv_count("monitor_number", parser, active_filter)
    print_csv_count("fullscreen", parser, active_filter)

    # for activity in parser.filter_by(active_filter):
    #     print activity["window_title"]
    

def print_csv_count(count_property, parser, filters={}):
    print(count_property)
    print("Category, Time Spent")
    for category, count in parser.count_by(count_property, filters).iteritems():
        print("{}, {}".format(category, count))

    print (",")


if __name__ == '__main__':
    main(parse_args())
