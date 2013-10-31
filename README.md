ahk_window_monitor
==================

A tool to monitor what programs you're using so you can see how much time you spend in different kinds of tasks

Requirements
------------
This project uses AutoHotkey and python. AutoHotkey is Windows only. It only uses the python standard library.

Setup
------------
clone the repo into a folder using 
git clone https://github.com/jpinsonault/ahk_window_monitor.git

To setup the AHK script, you'll have to edit the location of the output file. Towards the bottom of the file is the line:
C:\Users\joe\Documents\ahk_usage_tracker\window_log.txt

Just change the path to point to where you want the log file to be.

Usage
-----


track_window.ahk
----------------
This is a simple Autohotkey script that records the name of the active window as well as the timestamp and position of the window.
It outputs a CSV format file that can be used however you want

AHKLogParser.py
---------------
This module contains the AHKLogParser class which is used to pull useful and interesting data out of the log file
