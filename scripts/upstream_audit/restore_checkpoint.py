"""Restore only ordinary build outputs inside the isolated writable Lake cache."""

from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def validate_member(member):
    path = PurePosixPath(member.name)
    if (path.is_absolute() or ".." in path.parts or not path.parts
            or path.parts[0] != "build" or not (member.isdir() or member.isfile())):
        raise RuntimeError(f"Disallowed checkpoint member: {member.name}")


def main():
    process = subprocess.Popen(["zstd", "-dc", "/checkpoint/build.tar.zst"], stdout=subprocess.PIPE)
    total = 0
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                validate_member(member)
                total += member.size
                if total > 64 * 1024**3:
                    raise RuntimeError("Unpacked proof checkpoint exceeds 64 GiB")
                archive.extract(member, path=Path(".lake"), filter="data")
        if process.wait():
            raise RuntimeError("Checkpoint decompression failed")
    except BaseException:
        process.kill()
        process.wait()
        raise


if __name__ == "__main__":
    main()
