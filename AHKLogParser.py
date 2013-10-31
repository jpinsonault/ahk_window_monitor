import csv
import re
import time
from datetime import datetime


class AHKLogParser(object):
    """Contains functions for reading the AHK window log"""

    def __init__(self, log_filename):
        super(AHKLogParser, self).__init__()

        self.log_filename = log_filename

        self.log_fieldnames = ['timestamp', 'time_idle', 'window_title', 'width', 'height', 'x', 'y']

        self.log_dict = []
        self.read_log()

        self.activity_log = []
        self.parse_log()

    def read_log(self):
        with open(self.log_filename, 'r') as log_file:
            for line in csv.DictReader(log_file, fieldnames=self.log_fieldnames):
                self.log_dict.append(line)

    def print_dict(self):
        for line in self.log_dict:
            print(line)

    def parse_log(self):
        """
            The output of this will be a list that resembles the following:
                Active(bool), Classification(list of strings), Start Time(timestamp), Duration(seconds), Window Title(string), Fullscreen(bool), Monitor Number(int)
                e.g.:
                True, 15:34, 8, [Browser, Facebook], Chrome - Facebook, False, 1
                True, 15:42, 12, unkown, Introduction to the theory of computation, False, 0

            Active is true if the user has interacted with the computer recently
            Classification is the Manually supplied description of the app (Browser, A website name, Text editing, cmd window, etc)

            Fullscreen will be true if the height and width are the maximum resolution for the monitor
            Monitor number is the monitor the top-left of the window is on, always 0 if there's only one monitor
        """

        current_activity = None
        self.activity_log = []

        for log_line in self.log_dict:
            if current_activity is None:
                current_activity = Activity(log_line)

            elif current_activity.is_same(Activity(log_line)) == True:
                current_activity.increment_duration()

            else:
                self.activity_log.append(current_activity)
                current_activity = Activity(log_line)

    def save_parsed_output(self, filename):
        pass

    def get_idle(self):
        pass

    def get_active(self):
        pass

    def filter_by(self, filters={}):
        """
            Example filter object:
                {"active":True, "classification":["any", ["school", "facebook"]], "duration":["lt", 200]}
            Options:
                active: True/False
                    Was the user active during this activity

                classification: ["any/all", ["list", "of", "classifications"]]
                    any - If any of the classifiers match the activity matches
                    all - All the classifiers have to match
                    The second option is a list of classifiers to match against

                duration: ["lt/gt", length_in_seconds]
                    lt/gt stand for less/greater than or equal
                    The duration is the amount of time spent in the activity

                is_classified: True/False
                    Was the activity put into a category
        """
        filtered_data = []

        for activity in self.activity_log:
            if self.filter(activity, filters):
                filtered_data.append(activity)

        return filtered_data

    def filter(self, activity, filters):
        """returns true activity matches the filters"""

        match = True

        if "active" in filters:
            match = match and activity["active"] == filters["active"]
        if "classification" in filters:
            match = match and self.match_classifier(activity, filters)
        if "duration" in filters:
            match = match and self.match_duration(activity, filters)
        if "is_classified" in filters:
            match = match and activity.is_classified() == filters["is_classified"]

        return match

    def match_classifier(self, activity, filters):
        comparator = filters["classification"][0]
        class_filters = filters["classification"][1]
        classifier = activity["classification"]

        # Returns list of bools
        filter_results = [class_filter in classifier for class_filter in class_filters]

        if comparator == "all":
            return all(filter_results)
        elif comparator == "any":
            return any(filter_results)
        else:
            raise Exception("Invalid Comparator")

    def match_duration(self, activity, filters):
        comparator = filters["duration"][0]
        duration_filter = filters["duration"][1]
        activity_duration = activity.data["duration"]

        if comparator == "lt":
            return activity_duration <= duration_filter
        elif comparator == "gt":
            return activity_duration >= duration_filter
        else:
            raise Exception("Invalid Comparator")

    def count_by_classifications(self, filter_options={}):
        if filter_options:
            activity_log = self.filter_by(filter_options)
        else:
            activity_log = self.activity_log

        # counts = {classification: 0 for classification in Utils.classifications.keys()}
        counts = dict((classification, 0) for classification in Utils.classifiers.keys())
        counts["other"] = 0

        for activity in activity_log:
            for classification in activity["classification"]:
                counts[classification] += activity["duration"]

        return counts

    def count_by(self, count_property, filter_options={}):
        """
            Count the seconds spent doing something.
            count_property specifies the propery (classification, monitor_number, etc)
                you want use as the bins the time is added up in.
                
            For example, count the amount of time spent in different classifications of activities
                or the amount of time spent using one monitor or the other

            filter_options can further wittle down the activities you're looking at.
        """

        # Classifications is a special case
        if count_property == "classification":
            return self.count_by_classifications(filter_options)

        if filter_options:
            activity_log = self.filter_by(filter_options)
        else:
            activity_log = self.activity_log

        counts = {}

        for activity in activity_log:
            if activity[count_property] in counts:
                counts[activity[count_property]] += activity["duration"]
            else:
                counts[activity[count_property]] = activity["duration"]

        return counts


class Activity:
    """This class holds the data describing the activity and methods to work with the data"""
    def __init__(self, log_line):
        self.log_line = log_line

        self.data = {}
        self.data['active'] = Utils.is_active(log_line)
        self.data['classification'] = Utils.classify(log_line)
        self.data['start_time'] = log_line['timestamp']
        self.data['duration'] = 1
        self.data['window_title'] = log_line['window_title']
        self.data['fullscreen'] = Utils.is_fullscreen(log_line)
        self.data['monitor_number'] = Utils.get_monitor(log_line)

    def __getitem__(self, key):
        """Overloading index operator so Activity's can be treated like a dict"""
        return self.data[key]

    def is_same(self, other):
        """
            Compares this activity to the given activity.
            Returns true if considered the same, false otherwise
        """
        return (other.data['active'] == self.data['active'] and
            other.data['classification'] == self.data['classification'] and
            other.data['window_title'] == self.data['window_title'] and
            not self.check_long_pause(other))

    def check_long_pause(self, other):
        """
            Checks for a long pause between the timestamp of this activity 
            compared to the other activity
        """

        this_timestamp = time.mktime(time.strptime(self.data["start_time"], Utils.TIME_TEMPLATE)) + int(self.data["duration"]) - 1
        other_timestamp = time.mktime(time.strptime(other.data["start_time"], Utils.TIME_TEMPLATE))

        return other_timestamp - this_timestamp > Utils.LONG_PAUSE

    def is_classified(self):
        return len(self.data["classification"]) > 0

    def increment_duration(self):
        self.data["duration"] += Utils.GRANULARITY

    def get_dict(self):
        return self.data


class Utils:
    """
        Utility functions for parsing the log files
    """

    # Granularity of log file
    GRANULARITY = 1
    IDLE_THRESHOLD = 30000
    # 10/29/2013 16:14:40
    TIME_TEMPLATE = "%m/%d/%Y %H:%M:%S"
    LONG_PAUSE = 60*60*2

    classifiers = {
        "browser": r"(Google Chrome)|(Firefox)",
        "school": r"(CS 311)|(CS311)|(Quantified Life)|(PSU)|(Theory of Computation)",
        "command_line": r"(MINGW32)|(cmd.exe)",
        "text_editor": r"(Sublime Text)|(notepad)",
        "programming": r"(Sublime Text)|(Intellij)|(Android Developers)|(Python)|(ahk_usage_tracker)",
        "social": r"(Facebook)|(- chat -)",
        "entertainment": r"(reddit)|(imgur)",
        "chat": r"(- chat -)",
        "email": r"(- Gmail -)",
        "games": r"(Nexus Mod Manager)|(Steam)|(skyrim)|(max payne)",
        "stack_exchange": r"(Stack Overflow)",
        "search": r"(Google Search)",
        "system": r"(Task Switching)|(Start Menu)|(jdiskreport)|(Libraries)|(Documents)|(\d ((\w+) )*remaining)|(\(\w:\))|(dropbox)",
    }

    @staticmethod
    def is_active(log_line):
        return int(log_line['time_idle']) < Utils.IDLE_THRESHOLD

    @staticmethod
    def classify(log_line):
        classes = []

        window_title = log_line["window_title"]

        classes = [class_name for class_name, classifier in Utils.classifiers.iteritems()
            if Utils.match_classifier(window_title, classifier)]

        if not classes:
        	classes = ["other"]

        return classes

    @staticmethod
    def match_classifier(window_title, classifier):
        return re.search(classifier, window_title, re.IGNORECASE)

    @staticmethod
    def is_fullscreen(log_line):
        try:
            x = int(log_line["x"])
            y = int(log_line["y"])
        except ValueError:
            return False

        #  Check if the window is in the top left of either monitor
        return (x == -1448 and y == 98) or (x == -8 and y == -8)

    @staticmethod
    def get_monitor(log_line):
        # print("{}, {}".format(log_line["x"], log_line["x"] >= 0))
        try:
            if int(log_line["x"]) >= -8:
                return 0
            else:
                return 1
        except ValueError:
            return 0
