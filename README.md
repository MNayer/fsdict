# FSDict

## Design principles
1) Every key of a fsdict must be of type 'str' or 'FunctionType'.
2) A fsdict may not be part of a list.
3) A fsdict may contain other fsdicts.
4) Dictionaries in python are passed by reference; so are fsdicts. By default
an fsdict is always passed by refernece. That is, its values are not copied but
the fsdict is symlinked to the new position.

## Internals
Keys of type 'str' work just as normal dictionary keys. Keys of type
'FunctionType' are used as filters for the keys of an fsdict. So
```python
dictionary[lambda key: "foo" in key]
```
would return a generator which yields the values for keys which contain the
string 'foo'.

Possible value types and how they are handled:
- fsdict - a directory
- 'bytes' type - written to file as is
- any other python object (except for 'bytes') - pickled
