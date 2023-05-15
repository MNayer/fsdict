import json
from src.utils import *
from pathlib import Path


class fsdict:
    def __init__(self, path):
        self.path = Path(path)

    def __getitem__(self, key):
        if not self.has_key(key):
            raise KeyError(key)
        key_path = self.__get_keypath(key)
        if self.__is_fsdict(key):
            return fsdict(key_path)
        else:
            return maybe_deserialize(fread_bytes(key_path))

    def __setitem__(self, key, value):
        key_path = self.__get_keypath(key)
        if isinstance(value, fsdict):
            value.copy(key_path)
        else:
            fwrite_bytes(key_path, maybe_serialize(value))

    def __repr__(self):
        return json.dumps(self.todict(), indent=2)

    def todict(self, lazy=True):
        dictionary = dict()
        for key in self.keys():
            if self.__is_fsdict(key):
                key_path = self.__get_keypath(key)
                dictionary[key] = fsdict(key_path).todict(lazy)
                continue
            if lazy:
                dictionary[key] = "<lazy>"
            else:
                dictionary[key] = self[key]
        return dictionary

    def has_key(self, key):
        key_path = self.__get_keypath(key)
        return key_path.exists()

    def keys(self, lazy=False):
        keys = (keypath.name for keypath in self.__get_keypaths())
        if lazy:
            return keys
        else:
            return list(keys)

    def values(self, lazy=True):
        values = (self[key] for key in self.keys())
        if lazy:
            return values
        else:
            return list(values)

    def items(self):
        for key in self.keys():
            yield key, self[key]

    def copy(self, dst_path):
        symlink(self.path, dst_path)

    def __get_keypath(self, key):
        if not isinstance(key, str):
            raise TypeError(f"Value of key must be of type 'str' not '{type(key)}'")
        return self.path / key

    def __get_keypaths(self):
        return self.path.glob("*")

    def __is_fsdict(self, key):
        if not self.has_key(key):
            raise KeyError(key)
        key_path = self.path / key
        return key_path.is_dir()
