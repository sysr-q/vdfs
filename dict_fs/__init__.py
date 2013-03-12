import pprint

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
    def __init__(self, fs=None, env=None):
        if fs:
            self.fs = fs
        else:
            self.fs = {}

        if env:
            self.env = env
        else:
            self.env = {
                "PATH": "/usr/sbin:/sbin:/usr/local/bin:/usr/bin:/bin",
                "SHELL": "/bin/sh",
                "LANG": "C"
            }

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
        dir_list.extend([i for i in self.current_dictionary()])
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
            return True
        elif dir_name not in self.current_dictionary():
            return 3#CODE
        
        # The thing we're interested in "cd"ing into.
        dive_into = self.current_dictionary()[dir_name]

        if isinstance(dive_into, dict):
            self.current_dir.append(dir_name)
            return 0#CODE
        else:
            return 4#CODE

    def make_dir(self, dir_name):
        self.current_dictionary()[dir_name] = {}
        return True

    def touch(self, filename, contents=None):
        if not contents:
            contents = ""
        self.current_dictionary()[filename] = contents
        return True

    def print_debug_info(self, args):
        print "self.fs:"
        print pprint.pprint(self.fs)
        print "self.current_dictionary():"
        print self.current_dictionary()
        print "self.current_dir:"
        print self.current_dir

# Semi-implemented Debian-like FS dictionary.
pre_fs = {
    "": {
        "bin": {
            "sh": FS_BLOB,
            "cp": FS_BLOB
        },
        "dev": {
            "sda": FS_BLOB,
            "sda1": FS_BLOB
        },
        "etc": {
            "hosts": "\n".join([
                    "127.0.0.1 localhost",
                    "::1 ip6-localhost"
                ])
        },
        "home": {
            "user": {"docs": {}, "git": {}}
        },
        "sys": {},
        "tmp": {},
        "usr": {},
        "var": {}
    }
}

if __name__ == "__main__":
    # Really bad examples of use.
    
    fs = dict_fs(fs=pre_fs)
    for f in fs.list_dir():
        print f

    print "-"*50
    fs.change_dir("bin")
    for f in fs.list_dir():
        print f
    cd = fs.change_dir("cp") # A file
    print CODES[cd]

    fs.make_dir("test")
    fs.change_dir("test")

    print "-"*50
    fs.touch("example.txt")
    for f in fs.list_dir():
        print f
