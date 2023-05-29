import json
import types
from fsdict.utils import *
from pathlib import Path


class LazyValue:
    def __init__(self, basepath, path):
        self.basepath = basepath
        if isinstance(basepath, str):
            self.basepath = Path(basepath)
        self.path = path

    def __repr__(self):
        return f"<LazyValue {self.path} @ {self.basepath}>"

    def __str__(self):
        return repr(self)

    def read(self):
        # TODO
        raise NotImplementedError()


class genfsdict:
    def __init__(
        self, basepath=None, path="", overwrite=True, create_fsdict_on_keyerror=False
    ):
        self.basepath = Path(basepath) if basepath else None
        self.path = Path(path)
        self.overwrite = overwrite
        self.create_fsdict_on_keyerror = create_fsdict_on_keyerror
        if self.basepath != None and not self._fsdict_exists():
            self._create_empty_fsdict()

    def _fsdict_exists(self):
        raise NotImplementedError()

    def _del_item(self, key):
        raise NotImplementedError()

    def _is_fsdict(self, key):
        raise NotImplementedError()

    def _read_keyvalue(self, key):
        raise NotImplementedError()

    def _write_keyvalue(self, key, value):
        raise NotImplementedError()

    def _create_empty_fsdict(self, key=""):
        raise NotImplementedError()

    def _link_fsdict(self, key, other):
        raise NotImplementedError()

    def _has_key(self, key):
        return key in self.keys()

    def _get_item(self, key):
        assert not self.dangling()
        assert self._valid_keytype(key)
        if not self._has_key(key):
            if self.create_fsdict_on_keyerror:
                return self.__class__(
                    self.basepath,
                    self.path / key,
                    overwrite=self.overwrite,
                    create_fsdict_on_keyerror=self.create_fsdict_on_keyerror,
                )
            else:
                raise KeyError(key)
        if self._is_fsdict(key):
            return self.__class__(
                self.basepath,
                self.path / key,
                overwrite=self.overwrite,
                create_fsdict_on_keyerror=self.create_fsdict_on_keyerror,
            )
        return self._read_keyvalue(key)

    def _set_item(self, key, value):
        if self._has_key(key):
            if not self.overwrite:
                return
            del self[key]
        if isinstance(value, self.__class__):
            if value.dangling():
                self._create_empty_fsdict(key)
                return
            self._link_fsdict(key, value)
            return
        self._write_keyvalue(key, value)

    def _valid_keytype(self, key):
        return isinstance(key, str)

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        yield from self.keys()

    def __contains__(self, key):
        assert not self.dangling()
        assert self._valid_keytype(key)
        return self._has_key(key)

    def __getitem__(self, key):
        assert not self.dangling()
        return self._get_item(key)

    def __setitem__(self, key, value):
        assert not self.dangling()
        self._set_item(key, value)

    def __delitem__(self, key):
        assert not self.dangling()
        if not self._has_key(key):
            raise KeyError(key)
        self._del_item(key)

    def __repr__(self):
        return json.dumps(self.todict(), indent=2, default=repr)

    def keys(self):
        raise NotImplementedError()

    def todict(self, lazy=True):
        assert not self.dangling()
        dictionary = dict()
        for key in self.keys():
            if self._is_fsdict(key):
                dictionary[key] = self.__class__(
                    self.basepath,
                    self.path / key,
                    overwrite=self.overwrite,
                    create_fsdict_on_keyerror=self.create_fsdict_on_keyerror,
                ).todict(lazy)
                continue
            if lazy:
                dictionary[key] = LazyValue(self.basepath, self.path / key)
            else:
                dictionary[key] = self[key]
        return dictionary

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

    def dangling(self):
        return self.basepath == None

    def setpath(self, basepath):
        self.basepath = Path(basepath)


class fsdict(genfsdict):
    def _fsdict_exists(self):
        path = self.basepath / self.path
        return path.exists()

    def _del_item(self, key):
        key_path = self.basepath / self.path / key
        rm(key_path)

    def _is_fsdict(self, key):
        key_path = self.basepath / self.path / key
        return key_path.is_dir()

    def _read_keyvalue(self, key):
        key_path = self.basepath / self.path / key
        return maybe_deserialize(fread_bytes(key_path))

    def _write_keyvalue(self, key, value):
        key_path = self.basepath / self.path / key
        fwrite_bytes(key_path, maybe_serialize(value))

    def _create_empty_fsdict(self, key=""):
        key_path = self.basepath / self.path / key
        key_path.mkdir()

    def _link_fsdict(self, key, other):
        src_path = other.basepath / other.path
        dst_path = self.basepath / self.path / key
        symlink(src_path, dst_path)

    def _has_key(self, key):
        key_path = self.basepath / self.path / key
        return key_path.exists()

    def keys(self):
        assert not self.dangling()
        path = self.basepath / self.path
        keys = [keypath.name for keypath in path.glob("*")]
        return keys
