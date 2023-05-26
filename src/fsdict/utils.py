import os
import shutil
import pickle
import py7zr
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory


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
    if path.is_symlink():
        rmsymlink(path)
    if path.is_dir():
        rmtree(path)
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


def archive_exists(path):
    return path.exists() and path.is_file() and py7zr.is_7zfile(path)


def archive_create(fpath):
    with py7zr.SevenZipFile(fpath, "w") as archive:
        pass


def archive_has_member(fpath, path):
    return path in set(Path(p) for p in archive_getmembers(fpath))


def archive_member_isdir(fpath, path):
    with py7zr.SevenZipFile(fpath, "r") as archive:
        for info in archive.list():
            filename = Path(info.filename)
            if filename == path:
                return info.is_directory


def archive_member_isfile(fpath, path):
    return not archive_member_isdir(fpath, path)


def archive_member_issymlink(fpath, path):
    # with py7zr.SevenZipFile(fpath, "r") as archive:
    #    for info in archive.list():
    #        filename = Path(info.filename)
    #        if filename == path:
    #            return info.is_symlink
    raise NotImplementedError()


def archive_member_read(fpath, path):
    with py7zr.SevenZipFile(fpath, "r") as archive:
        return archive.read([str(path)])[str(path)].read()


def archive_member_write(fpath, path, data):
    with py7zr.SevenZipFile(fpath, "a") as archive:
        archive.writef(BytesIO(data), arcname=str(path))


def archive_member_createdir(fpath, path):
    with TemporaryDirectory() as directory:
        dirpath = Path(directory)
        fqpath = dirpath / path
        fqpath.mkdir(parents=True)
        with py7zr.SevenZipFile(fpath, "a") as archive:
            archive.writeall(fqpath, arcname=path)


def archive_getmembers(fpath):
    with py7zr.SevenZipFile(fpath, "r") as archive:
        return archive.getnames()
