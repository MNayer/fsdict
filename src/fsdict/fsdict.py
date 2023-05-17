import json
import types
from fsdict.utils import *
from pathlib import Path


class LazyValue:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f"<LazyValue @ {self.path}>"

    def __str__(self):
        return repr(self)

    def read(self):
        return maybe_deserialize(fread_bytes(self.path))


class fsdict:
    def __init__(self, path=None, overwrite=True):
        self.path = Path(path) if path else None
        self.overwrite = overwrite
        if self.path != None:
            if not self.path.exists():
                self.path.mkdir()
            assert self.path.is_dir()

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        yield from self.keys()

    def __contains__(self, key):
        assert not self.dangling()
        assert isinstance(key, str)
        key_path = self.__get_path(key)
        return key_path.exists()

    def __getitem__(self, selector):
        assert not self.dangling()
        if isinstance(selector, str):
            return self.__get_item(selector)
        elif isinstance(selector, types.FunctionType):
            return self.__get_items(selector)

    def __setitem__(self, selector, value):
        assert not self.dangling()
        if isinstance(selector, str):
            self.__set_item(selector, value)
        elif isinstance(selector, types.FunctionType):
            self.__set_items(selector, value)

    def __delitem__(self, selector):
        assert not self.dangling()
        if isinstance(selector, str):
            self.__del_item(selector)
        elif isinstance(selector, types.FunctionType):
            self.__del_items(selector)

    def __repr__(self):
        return json.dumps(self.todict(), indent=2, default=repr)

    def __get_item(self, key):
        assert not self.dangling()
        assert isinstance(key, str)
        key_path = self.__get_path(key)
        if not key_path.exists():
            raise KeyError(key_path.name)
        if self.__is_fsdict(key):
            return fsdict(key_path)
        else:
            return maybe_deserialize(fread_bytes(key_path))

    def __get_items(self, selector):
        assert not self.dangling()
        assert isinstance(selector, types.FunctionType)
        keys = filter(selector, self.keys())
        yield from (self[key] for key in keys)

    def __set_item(self, key, value):
        key_path = self.__get_path(key)
        if key_path.exists():
            if not self.overwrite:
                return
            del self[key]
        if isinstance(value, fsdict):
            if value.dangling():
                key_path.mkdir()
            else:
                value.copy(key_path)
        else:
            fwrite_bytes(key_path, maybe_serialize(value))

    def __set_items(self, selector, value):
        assert not self.dangling()
        assert isinstance(selector, types.FunctionType)
        keys = filter(selector, self.keys())
        for key in keys:
            self[key] = value

    def __del_item(self, key):
        assert not self.dangling()
        key_path = self.__get_path(key)
        if key_path.exists():
            rm(key_path)

    def __del_items(self, selector):
        assert not self.dangling()
        assert isinstance(selector, types.FunctionType)
        keys = filter(selector, self.keys())
        for key in keys:
            del self[key]

    def dangling(self):
        return self.path == None

    def setpath(self, path):
        self.path = Path(path)

    def todict(self, lazy=True):
        assert not self.dangling()
        dictionary = dict()
        for key in self.keys():
            key_path = self.__get_path(key)
            if self.__is_fsdict(key):
                dictionary[key] = fsdict(key_path).todict(lazy)
                continue
            if lazy:
                dictionary[key] = LazyValue(key_path)
            else:
                dictionary[key] = self[key]
        return dictionary

    def keys(self, lazy=False):
        assert not self.dangling()
        keys = (keypath.name for keypath in self.__get_paths())
        if lazy:
            return keys
        else:
            return list(keys)

    def values(self, lazy=True):
        assert not self.dangling()
        values = (self[key] for key in self.keys())
        if lazy:
            return values
        else:
            return list(values)

    def items(self):
        assert not self.dangling()
        for key in self.keys():
            yield key, self[key]

    def copy(self, dst_path):
        assert not self.dangling()
        symlink(self.path, dst_path)

    def __get_path(self, key):
        assert not self.dangling()
        if isinstance(key, str):
            return self.path / key
        raise TypeError(f"Value of key '{key}' must be of type 'str' not '{type(key)}'")

    def __get_paths(self):
        assert not self.dangling()
        return self.path.glob("*")

    def __is_fsdict(self, key):
        assert not self.dangling()
        if not key in self:
            raise KeyError(key)
        key_path = self.path / key
        return key_path.is_dir()
