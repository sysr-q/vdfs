import pprint

FS_BLOB = "__DICT_FS_BLOB__"
FS_FILE = "__DICT_FS_FILE__"
FS_DIR = "__DICT_FS_DIR__"


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

    def current_dictionary(self):
        d = self.fs[""]
        for key in self.current_dir:
            d = d[key]
        return d

    def ls(self, args):
        print "Contents of directory:", "/" + ("/".join(self.current_dir)) + ":"
        for i in self.current_dictionary():
            print i

    def cd(self, args):
        if len(args) != 1:
            print "Usage: cd <directory>"
            return

        if args[0] == "..":
            if len(self.current_dir) == 0:
                print "Can't go above root."
            else:
                self.current_dir.pop()
            return
        elif args[0] not in self.current_dictionary():
            print "Directory", args[0], "not found"
            return
        
        # The thing we're interested in "cd"ing into.
        dive_into = self.current_dictionary()[args[0]]

        if isinstance(dive_into, dict):
            self.current_dir.append(args[0])
        else:
            print "Not a directory:", args[0]

    def mkdir(self, args):
        if len(args) != 1:
            print "Usage: mkdir <directory>"
            return
        self.current_dictionary()[args[0]] = {}

    def info(self, args):
        print "self.fs:"
        print pprint.pprint(self.fs)
        print "self.current_dictionary():"
        print self.current_dictionary()
        print "self.current_dir:"
        print self.current_dir

    def handle(self, params):
        commands = {'ls': self.ls, 'cd': self.cd, 'mkdir': self.mkdir, 'info': self.info}
        cmd = params.split()[0]
        if cmd in commands:
            commands[cmd](params.split()[1:])

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
            "hosts": "\n".join(
                [
                    "127.0.0.1 localhost",
                    "::1 ip6-localhost"
                ]
            )
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
    fs = dict_fs(fs=pre_fs)
    while True:
        raw = raw_input("> ")
        if raw == "break":
            break
        fs.handle(raw)
    print "\nGoodbye!"