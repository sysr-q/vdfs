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

LOOKUP = {}


def resolve(inode):
    if inode not in LOOKUP:
        return None
    return LOOKUP[inode]


class DictFsBase(object):
    def __init__(self, name=None, add_to_lookup=True):
        self.name = name
        # Guaranteed randomness, or your money back!
        self.inode = uuid.uuid4().hex
        # inode of our parental object
        self.parent = None
        if add_to_lookup:
            LOOKUP[self.inode] = self
        self.seperator = "/"


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
    def tree_root(self, lookup=True):
        """ Recurse back up the file tree, to try
            and find the "root" of this object.
            This will be represented by an object
            without a parent; either the Filesystem or
            whatever object owns this without a parent.

            If there is no parent, return this object.
        """
        parent = self.parent
        if parent is None:
            return self
        parobj = resolve(parent)
        while parobj.parent is not None:
            parent = parobj.parent
            parobj = resolve(parent)
        if lookup:
            return resolve(parobj.inode)
        return parobj.inode

    @property
    def path(self):
        """ Recurses back up the chain, creating a
            back to front list of parents up to the root.

            Reverse the list, join it with some seperators
            and you're good to go!
        """
        root = self.tree_root
        sep = root.seperator
        path = []
        if root is not self:
            # If we're not the root, we should
            # append our name to the list.
            path.append(self.name)
        parent = self.parent
        if parent is None:
            return sep + sep.join(path[::-1])

        parobj = resolve(parent)
        while parobj.parent is not None:
            if parobj is not root:
                # We don't want to append the name of the FS root.
                path.append(parobj.name)
            parent = parobj.parent
            parobj = resolve(parent)
        return sep + sep.join(path[::-1])

    def child(self, ident):
        for i, c in self.children().items():
            if c.inode == ident or c.name == ident:
                return c
        raise NoSuchChild("No such child identified by: {0}".format(ident))
    __call__ = child

    def give_child(self, child):
        if child.inode in self.children():
            err = "This parent already has a child identified by: {0}"
            raise ChildAlreadyPresent(err.format(child.inode))
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
    def __init__(self,
                 perms=None,
                 bit=None,
                 uid=None,
                 gid=None,
                 ctime=None,
                 size=None,
                 **kwargs):
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
        r = "<{cls}, {name} @{inode}, children: {children}, {perms}>"
        clen = len(self.children()) if self._children is not None else None
        return r.format(
            cls=self.__class__.__name__,
            name=self.name,
            inode=self.inode,
            # "None" or number of children.
            children=clen,
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


class urandom(File):
    """ Pretends to be /dev/urandom - sort of so you can set this
        for binary blob-like files.
    """
    def __init__(self, length=1024, **kwargs):
        super(urandom, self).__init__(**kwargs)
        self.length = length
        self.data = self._crud()

    def _crud(self):
        import random
        return "".join([
            chr(random.randint(0, 255)) for _ in xrange(self.length)
        ])
