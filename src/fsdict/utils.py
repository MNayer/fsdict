import os
import shutil
import pickle


def fwrite(path, data):
    with open(path, "w") as f:
        f.write(data)


def fwrite_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def fread(path, data):
    with open(path, "r") as f:
        return f.read()


def fread_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def copy(src, dst):
    shutil.copytree(src, dst, dirs_exist_ok=True)


def rmtree(path):
    shutil.rmtree(path)


def rmfile(path):
    os.remove(path)


def rmsymlink(path):
    os.unlink(path)


def rm(path):
    if path.is_dir():
        rmtree(path)
    if path.is_symlink():
        rmsymlink(path)
    if path.is_file():
        rmfile(path)


def symlink(src, dst):
    os.symlink(src, dst)


def serialize(obj):
    return pickle.dumps(obj)


def deserialize(data):
    return pickle.loads(data)


def maybe_serialize(obj):
    if isinstance(obj, bytes):
        return obj
    return serialize(obj)


def maybe_deserialize(data):
    try:
        return deserialize(data)
    except (pickle.UnpicklingError, EOFError):
        return data
