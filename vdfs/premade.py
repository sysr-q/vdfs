# -*- coding: utf-8 -*-

import vdfs

def create(d):
    fs = vdfs.Filesystem()
    for k, v in d.iteritems():
        fs.give_child(create_from_dict(k, v))
    return fs

def create_from_dict(k, v):
    """ Recurses down a tree of a dictionary, and creates a
        corresponding vdfs filesystem. "The heavy lifter"
    """
    if v is Blob:
        return vdfs.File(name=k, data="HOLY_FUCKING_SHIT")
    if isinstance(v, basestring):
        return vdfs.File(name=k, data=v)
    if hasattr(v, "__iter__"):
        f = vdfs.Directory(name=k)
        for k1, v1 in v.iteritems():
            f.give_child(create_from_dict(k1, v1))
        return f

class Blob(object):
    pass

fs_debian_like = {
    "bin": {
        "sh": Blob,
        "cp": Blob,
    },
    "dev": {
        "sda": Blob,
        "sda1": Blob
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