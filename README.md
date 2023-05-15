# FSDict

## Design principles
1) Every key of a fsdict must be of type 'str'.
2) A fsdict may not be part of a list.
3) A fsdict may contain other fsdicts.
4) Dictionaries in python are passed by reference; so are fsdicts. By default
an fsdict is always passed by refernece. That is, its values are not copied but
the fsdict is symlinked to the new position.

## Internals
Possible value types and how they are handled:
- fsdict - a directory
- 'bytes' type - written to file as is
- any other python object (except for 'bytes') - pickled
