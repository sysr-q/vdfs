# -*- coding: utf-8 -*-
import vdfs


def create(d):
    """ Recurses down a tree of a dictionary and creates a
        corresponding vdfs filesystem.
    """
    fs = vdfs.Filesystem()
    for k, v in d.iteritems():
        fs.give_child(create_from_dict(k, v))
    return fs


def create_from_dict(k, v):
    """ Recurses down a tree of a dictionary, and creates a
        corresponding vdfs filesystem. "The heavy lifter".

        If a given string has a value of "__RANDOM_DATA_HERE__",
        it will be given a class of vdfs.urandom() instead.
        Other strings are given a class of vdfs.File, and
        things that have a value of a dictionary get a vdfs.Directory
    """
    if v is "__RANDOM_DATA_HERE__":
        return vdfs.urandom(name=k)
    if isinstance(v, basestring):
        return vdfs.File(name=k, data=v)
    if hasattr(v, "__iter__"):
        f = vdfs.Directory(name=k)
        for k1, v1 in v.iteritems():
            f.give_child(create_from_dict(k1, v1))
        return f

fs_debian_like = {
    "bin": {
        "sh": "__RANDOM_DATA_HERE__",
        "cp": "__RANDOM_DATA_HERE__"
    },
    "dev": {
        "sda": "__RANDOM_DATA_HERE__",
        "sda1": "__RANDOM_DATA_HERE__"
    },
    "etc": {
        "hosts": "\n".join([
            "127.0.0.1 localhost",
            "::1 ip6-localhost"
        ])
    },
    "home": {
        "john": {
            "docs": {
            },
            "git": {
                "deep": "DURRHURR"
            }
        }
    },
    "sys": {},
    "tmp": {},
    "usr": {},
    "var": {}
}