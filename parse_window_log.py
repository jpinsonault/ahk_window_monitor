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

    # Example filters

    # Active means the user was not idle
    active_filter = {
        "active": True
    }

    # classification is the category of activity
    browser_filter = {
        "active": True,
        "classification": ['any', ['browser']]
    }

    # Adds the restriction that the program must be fullscreen
    fullscreen_browser_filter = {
        "active": True,
        "classification": ['any', ['browser']],
        "fullscreen": True
    }

    # The 'any' keyword means either of the categories in 
    # ['social', 'entertainment'] can match
    # 
    # 'all' would mean it has to match both
    social_entertainmnt_filter = {
        "active": True,
        "classification": ['any', ['social', 'entertainment']],
    }


    # print_csv_count will print out a csv format file you can redirect to a file,
    # and then open in excel/google drive
    # 
    # The first argument is basically the type of bucket the function will collect
    # time into. If you specify a filter, those restrictions will be applied to the data
    print_csv_count("classification", parser, active_filter)
    print_csv_count("classification", parser, browser_filter)
    print_csv_count("active", parser)
    print_csv_count("monitor_number", parser, active_filter)
    print_csv_count("fullscreen", parser, active_filter)

    # for activity in parser.filter_by(active_filter):
    #     print activity["window_title"]
    

def print_csv_count(count_property, parser, filters={}):
    print("Category, Time Spent (seconds)")
    for category, count in parser.count_by(count_property, filters).iteritems():
        print("{}, {}".format(category, count))

    print (",")


if __name__ == '__main__':
    main(parse_args())
