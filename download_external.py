
import os
import sys
import hashlib
import zipfile
import platform
import argparse
import subprocess
import urllib.request


dependency = {
    "CMakeModules": {
        "file": "CMakeModules@1.28.trunk.31965103.7z",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "7eb7cd4cf029ae3b2fa8206511d0cb13",
    },
    "rapidjson": {
        "file": "rapidjson@1.1.0-67fac85-073453e1.7z",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "cebce7f986c4505568e8e7c47fcaccdc",
    },
    "clang-physxmetadata": {
        "file": "clang-physxmetadata@4.0.0.31968624_1.1.7z",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "d8fc156c7c5db89d486da234bade4b3b",
    },
    "freeglut-windows": {
        "file": "freeglut-windows@3.4_1.1.7z",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "53c4bee83f386beb837f68d0d468f419",
    },
    "opengl-linux": {
        "file": "opengl-linux@2017.5.19.1.7z",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "356e2046346080cfc739e05e69e6736f",
    },
    "PhysXDevice": {
        "file": "PhysXDevice@18.12.7.3.7z",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "7bb668cfab0dd298f00e746c94ce7003",
    },
    "PhysXGpu": {
        "file": "PhysXGpu@104.1-5.1.1151.32112585-public.zip",
        "url": "https://d4i3qtqj3r0z5.cloudfront.net/",
        "md5": "c78c177a825e2771739a55f2d9402c72",
    },
}


ROOT = os.path.dirname(os.path.abspath(__file__))


def get_7z():
    file = "7za@16.02.4.zip"
    url = "https://bootstrap.packman.nvidia.com/"
    md5 = "df8c71fbba63a6d2c1d98fbdfa805f78"

    unpacked = _extract_to(file)
    if not checksum(file, md5) or not os.path.isdir(unpacked):
        archived = download(url, file)
        print("-- Unzipping: %s" % archived)
        with zipfile.ZipFile(archived, 'r') as zip_ref:
            zip_ref.extractall(unpacked)

    bitness = "64" if sys.maxsize > 2**32 else "32"

    if platform.system() == "Windows":
        return os.path.join(unpacked, "win-x86", bitness, "7za.exe")
    elif platform.system() == "Darwin":
        return os.path.join(unpacked, "mac-x86", bitness, "7za")
    else:
        return os.path.join(unpacked, "linux-x86", bitness, "7za")


def get_upx():
    version = "4.0.1"
    url = "https://github.com/upx/upx/releases/download/v%s/" % version
    if platform.system() == "Windows":
        file = "upx-%s-win64.zip" % version
        md5 = "acf37b08b0788a640edb25e4de6edca9"
        dst = _extract_to(file, "upx")
        upx = os.path.join(dst, "upx-%s-win64" % version, "upx.exe")
    else:
        file = "upx-%s-i386_linux.tar.xz" % version
        md5 = "a36817c86da90a323eb35430f9707074"
        dst = _extract_to(file, "upx")
        upx = os.path.join(dst, "upx-%s-i386_linux" % version, "upx")

    archived = _download_to(file)
    if not checksum(file, md5) or not os.path.isdir(dst):
        download(url, file)
        print("-- Unzipping:   %s" % archived)
        if not os.path.isdir(dst):
            os.makedirs(dst)
        subprocess.check_call(["tar", "-xf", archived], cwd=dst)

        if platform.system() == "Linux":
            subprocess.check_call(["chmod", "+x", upx])

    return upx


def _download_to(file):
    dir_path = os.path.join(ROOT, "download")
    dest = os.path.join(dir_path, file)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return dest


def _extract_to(file, dirname=None):
    name = dirname or file.split("@")[0]
    return os.path.join(ROOT, "external", name)


def download(url, file):
    archived = _download_to(file)
    print("-- Downloading: %s" % archived)
    filename, _ = urllib.request.urlretrieve(url + file, archived)
    return filename


def checksum(file, md5):
    file_path = _download_to(file)
    if not os.path.isfile(file_path):
        return False
    with open(file_path, "rb") as fp:
        return hashlib.md5(fp.read()).hexdigest() == md5


def obtain(url, file, md5):
    extractor = get_7z()
    archived = _download_to(file)
    unpacked = _extract_to(file)
    if not checksum(file, md5) or not os.path.isdir(unpacked):
        download(url, file)
        print("-- Unzipping:   %s" % archived)
        if not os.path.isdir(unpacked):
            os.makedirs(unpacked)
        subprocess.check_call([extractor, "x", "-bso0", "--", archived],
                              cwd=unpacked)


def compress_gpu(config):
    config = config.lower()
    if config not in ("checked", "profile", "release"):
        config = "checked"

    unpacked = _extract_to("PhysXGpu")
    if platform.system() == "Windows":
        target = "win.x86_64.vc141.mt"
        file = "PhysXGpu_64.dll"
    else:
        target = "linux.clang"
        file = "libPhysXGpu_64.so"

    lib = os.path.join(unpacked, "bin", target, config, file)
    upx = get_upx()
    print("-- About to compress GPU lib: %s" % lib)
    return_code = subprocess.call([upx, "-t", "-qq", lib])
    if return_code:
        print("-- Compressing GPU lib, this may take a few minutes...")
        subprocess.call([upx, lib])
    else:
        print("-- GPU lib already been compressed.")


def main(gpu_enabled, config):
    gpu_enabled = gpu_enabled and platform.system() != "Darwin"

    for name, d in dependency.items():
        if not gpu_enabled and name in ("PhysXGpu", "PhysXDevice"):
            continue
        obtain(d["url"], d["file"], d["md5"])

    if gpu_enabled:
        compress_gpu(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", default=False, action="store_true")
    parser.add_argument("--config", default="release")

    args = parser.parse_args()
    main(args.gpu, args.config)
