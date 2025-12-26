import os
import sys
import tarfile, urllib.request, pathlib
import subprocess

InitDir = "/home/admin/env/"
ProjectDir = "/home/admin/env/glm"
OldProjectDir = f"{ProjectDir}_old"
TempProjectDir = "/home/admin/env/download/glm"
DownloadDir = "/home/admin/env/download"
TarFilename = "glm.tar.gz"

def install_tar_url(url: str, *, interpreter=sys.executable):
    """下载 tar.gz"""

    os.chdir(InitDir)
    os.rmdir(DownloadDir)
    os.mkdir(DownloadDir)
    tar_path = pathlib.Path(DownloadDir) / "glm.tar.gz"
    print("Downloading", url)
    urllib.request.urlretrieve(url, tar_path)

    print("Extracting...")
    os.chdir(DownloadDir)
    with tarfile.open(tar_path, "r:gz") as tf:
        tf.extractall(DownloadDir)
    os.chdir(InitDir)
    # 链接与清理
    os.remove(OldProjectDir)
    os.rename(OldProjectDir, ProjectDir)
    os.rename(ProjectDir, TempProjectDir)
    os.chdir(ProjectDir)
    subprocess.check_call([interpreter, "-m", "pip", "install", "-r", "requirements.txt", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "--trusted-host", "pypi.tuna.tsinghua.edu.cn"])


def check_env(version, url):
    data = ""
    versionUrl = url + f"_{version}"
    try:
        os.chdir(ProjectDir)
        data = open("version.txt").read().strip()
        if str(data) != version:
            install_tar_url(versionUrl)
    except Exception as e:
        install_tar_url(versionUrl)

if __name__ == "__main__":
    # 硬编码的参数： serial, label, otp, menoy
    url = "http://"
    version = otp
    check_env(version, url)
    os.chdir(ProjectDir)
    import main
    main.main(serial, label, "", menoy)
