# -*- coding: utf-8 -*-
import time


class DictFSException(Exception):
    pass

class NoSuchChild(DictFSException):
    pass

class NoNameGiven(DictFSException):
    pass

class ChildAlreadyPresent(DictFSException):
    pass

class NotAllowedChildren(DictFSException):
    pass

#-----------------

class DictFsBase(object):
    def __init__(self, name=None):
        self._name = name

class ParentWithChild(DictFsBase):
    """ An abstracted class which provides a
        "parent" object, as well as a dictionary
        of "children" objects.
    """
    def __init__(self, name=None, parent=None, children=None):
        self._name = name
        self._parent = parent
        self._children = children or {}

    @property
    def root_filesystem(self):
        """ Recurse back up the file tree, to try
            and find the "root" of this object.
            This will be represented by an object
            without a parent; either the Filesystem or
            whatever object owns this without a parent.
        """
        p = self._parent
        if p is None:
            return None
        while p._parent is not None:
            p = p._parent
        return p

    def child(self, name):
        if name in self._children:
            return self._children[name]
        raise NoSuchChild("No such child named: {0}".format(name))

    def give_child(self, child):
        if child._name in self._children:
            raise ChildAlreadyPresent("This parent already has a child named: {0}".format(child._name))
        child._parent = self
        self._children[child._name] = child

    def children(self):
        return self._children

    def __repr__(self):
        return "<{cls}#{name}, children: {children}>".format(
            cls=self.__class__.__name__,
            name=self._name,
            children=len(self.children())
        )

    """ Bad hacky implementation to call fs.test instead of fs.child('test')
    def __getattr__(self, name):
        if name in self.__dict__['children']:
            return self.__dict__['children'][name]
        raise AttributeError
    """

class ParentChildPermissions(ParentWithChild):
    def __init__(self, perms=None, bit=None, uid=None, gid=None, ctime=None, size=None, **kwargs):
        super(ParentChildPermissions, self).__init__(**kwargs)
        self._perms = perms or "rw-r--r--"
        self._bit = bit or "-"
        self._uid = uid
        self._gid = gid
        self._time = ctime or int(time.time())
        self._size = size

    @property
    def perms(self):
        return "{0}{1}".format(self._bit, self._perms)

    def __repr__(self):
        return "<{cls}#{name}, children: {children}, {perms}>".format(
            cls=self.__class__.__name__,
            name=self._name,
            # "None" or number of children.
            children=len(self.children()) if self._children is not None else None,
            perms=self.perms
        )

class Filesystem(ParentWithChild):
    """ The root file system.

        This relates to /, or whatever the root of your
        fake file system is.
    """
    def __init__(self, **kwargs):
        super(Filesystem, self).__init__(**kwargs)
        self._name = "root"
        # The root has no parent.
        self._parent = None

    @staticmethod
    def from_dict(self, d):
        pass

class Directory(ParentChildPermissions):
    """ A folder/directory object.
        Similar to the filesystem, has a
        dictionary of "children" objects.
    """
    def __init__(self, perms=None, **kwargs):
        super(Directory, self).__init__(**kwargs)
        self._perms = perms or "rwxr-xr-x"
        self._bit = "d"

class File(ParentChildPermissions):
    """ This can represent binary data,
        a file in text/plain, anything!

        Should be parented by a directory,
        and can't own directories or other blobs.
    """
    def __init__(self, data=None, perms=None, **kwargs):
        super(File, self).__init__(**kwargs)
        self.data = data
        self._perms = perms or "rw-r--r--"
        self._children = None

    def give_child(self, *args, **kwargs):
        raise NotAllowedChildren("Files are unable to store children")

    def children(self):
        raise NotAllowedChildren("Files are unable to store children")