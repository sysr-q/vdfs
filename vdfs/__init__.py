# -*- coding: utf-8 -*-
import time
import uuid


class DictFSException(Exception):
    """ The base exception for VDFS errors.
        All other errors are children of this,
        easily allowing you to blanket-catch
        them all.
    """
    pass

class NoSuchChild(DictFSException):
    """ You attempted to access a child which this
        object does not parent.
    """
    pass

class NoNameGiven(DictFSException):
    """ You didn't give the required name field to
        this object.

        Not really used, but may be implemented at a
        later time, since it makes sense.
    """
    pass

class ChildAlreadyPresent(DictFSException):
    """ This object already parents a child of the
        given child's name.
    """
    pass

class NotAllowedChildren(DictFSException):
    """ You attempted to give a child to an object
        which isn't allowed to be a parent.
    """
    pass

#-----------------

MASTER = {}

class DictFsBase(object):
    def __init__(self, name=None):
        self.name = name
        # Guaranteed randomness, or your money back!
        self.inode = uuid.uuid4().hex
        # inode of our parental object
        self.parent = None

class ParentWithChild(DictFsBase):
    """ An abstracted class which provides a
        "parent" object, as well as a dictionary
        of "children" objects.
    """
    def __init__(self, name=None, parent=None, children=None):
        super(ParentWithChild, self).__init__(name=name)
        self.name = name
        if isinstance(parent, DictFsBase):
            self.parent = parent.inode
        else:
            self.parent = parent
        self._children = children or {}

    @property
    def tree_root(self):
        """ Recurse back up the file tree, to try
            and find the "root" of this object.
            This will be represented by an object
            without a parent; either the Filesystem or
            whatever object owns this without a parent.

            If there is no parent, return this object.
        """
        raise NotImplemented('Disfunctional until rewrite, due to inode system.')
        p = self.parent
        if p is None:
            return self
        while p.parent is not None:
            p = p.parent
        return p

    @property
    def path(self):
        """ Recurses back up the chain, creating a
            back to front list of parents up to the root.

            Reverse the list, join it with some seperators
            and you're good to go!
        """
        raise NotImplemented('Disfunctional until rewrite, due to inode system.')

        root = self.tree_root
        sep = root.seperator
        path = []
        if root is not self:
            # If we're not the root, we should
            # append our name to the list.
            path.append(self.name)
        p = self.parent
        if p is None:
            return sep + sep.join(path[::-1])

        while p.parent is not None:
            path.append(p.name)
            p = p.parent
        return sep + sep.join(path[::-1])

    def child(self, ident):
        for i, c in self.children().items():
            if c.inode == ident or c.name == ident:
                return c
        raise NoSuchChild("No such child identified by: {0}".format(ident))

    def give_child(self, child):
        if child.inode in self.children():
            raise ChildAlreadyPresent("This parent already has a child identified by: {0}".format(child.inode))
        child.parent = self.inode
        self._children[child.inode] = child

    def take_child(self, ident):
        if ident not in self.children():
            raise NoSuchChild("No such child identified by: {0}".format(inode))
        return self._children.pop(ident)

    def children(self):
        return self._children

    def __repr__(self):
        return "<{cls}, {name} @{inode}, children: {children}>".format(
            cls=self.__class__.__name__,
            name=self.name,
            inode=self.inode,
            children=len(self.children())
        )

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
        return "<{cls}, {name} @{inode}, children: {children}, {perms}>".format(
            cls=self.__class__.__name__,
            name=self.name,
            inode=self.inode,
            # "None" or number of children.
            children=len(self.children()) if self.children() is not None else None,
            perms=self.perms
        )

class Filesystem(ParentWithChild):
    """ The root file system.

        This relates to /, or whatever the root of your
        fake file system is.
    """
    def __init__(self, **kwargs):
        super(Filesystem, self).__init__(**kwargs)
        self.name = "root"
        # The root has no parent.
        self.parent = None
        self.seperator = "/"

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

def debug_filesystem():
    """ Throws together a little filesystem to enable quick
        debugging without having to manually create one.
    """
    fs = Filesystem()
    d = Directory(name="System")
    fs.give_child(d)
    fs.child('System').give_child(File(name="test"))
    fs.give_child(Directory(name="Users"))
    fs.child('Users').give_child(Directory(name="Anon"))
    fs.child('Users').child('Anon').give_child(
        File(name="work", data="1. Be cool.\n2. Lrn 2 hack.")
    )
    return fs