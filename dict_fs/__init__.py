# -*- coding: utf-8 -*-
import pprint
import re

FS_BLOB = "__DICT_FS_BLOB__"
FS_FILE = "__DICT_FS_FILE__"
FS_DIR = "__DICT_FS_DIR__"

CODES = {
    0: "All according to plan",
    1: "change_dir(): given non-string as directory name",
    2: "change_dir(): already in root directory",
    3: "change_dir(): directory non-existent",
    4: "change_dir(): given directory name isn't a directory"
}


class dict_fs(object):
    def __init__(self, fs=None):
        if fs:
            self.fs = fs
        else:
            self.fs = {}

        self.current_dir = []

        self.root_name = "/" # C:\, whatever.
        self.sep = "/"

    def current_dictionary(self):
        d = self.fs[""]
        for key in self.current_dir:
            d = d[key]
        return d

    def list_dir(self, dir_name=None):
        dir_list = []
        dir_list.append("Contents of directory: " +  self.root_name + (self.sep.join(self.current_dir)) + ":")
        dir_list.extend(sorted([i for i in self.current_dictionary()]))
        return dir_list

    def is_root_dir(self):
        return len(self.current_dir) == 0

    def change_dir(self, dir_name):
        if not isinstance(dir_name, basestring):
            return 1#CODE

        if dir_name == "..":
            if self.is_root_dir():
                return 2#CODE
            else:
                self.current_dir.pop()
            return 0
        elif not self.exists(dir_name):
            return 3#CODE
        
        # The thing we're interested in "cd"ing into.
        dive_into = self.current_dictionary()[dir_name]

        if isinstance(dive_into, dict):
            self.current_dir.append(dir_name)
            return 0#CODE
        else:
            return 4#CODE

    def exists(self, name):
        return name in self.current_dictionary()

    def make_dir(self, dir_name):
        if self.exists(dir_name):
            return False
        self.current_dictionary()[dir_name] = {}
        return True

    def touch(self, filename, contents=None):
        if self.exists(filename):
            return False

        if not contents:
            contents = ""
        self.current_dictionary()[filename] = contents
        return True