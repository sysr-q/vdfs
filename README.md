vdfs
====
Virtual Dictionary Filesystem. That's what this is.

VDFS is a small proof-of-concept implementation for an in memory file system made of dictionaries.  
The root is represented by a `vdfs.Filesystem`, which can be the parent of directories and files.
Directories can recursively parent files or other directories, ad infinitum.  
As per a real file system, a file __can't__ parent anything else. It's just a chunk of data.

Since this is a relatively new project, there isn't really any documentation, and the syntax isn't set in stone.
Have a little read of the source if you're interested in working with it, though.