import os
import sys
import shutil
import tarfile, urllib.request, pathlib
import subprocess

InitDir = "/home/admin/env/"
ProjectDir = f"{InitDir}/glm"
OldProjectDir = f"{ProjectDir}_old"
TempProjectDir = f"{InitDir}/download/glm"
DownloadDir = f"{InitDir}/download"
TarFilename = "glm.tar.gz"

def install_tar_url(url: str, *, interpreter=sys.executable):
    """下载 tar.gz"""

    os.chdir(InitDir)
    try:
        shutil.rmtree(DownloadDir)
    except Exception as e:
        pass
    finally:
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
    try:
        shutil.rmtree(OldProjectDir)
    except:
        pass

    try:
        os.rename(ProjectDir, OldProjectDir)
    except Exception as e:
        pass
    os.rename(TempProjectDir, ProjectDir)
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
    url = "http://118.31.111.114:8080/filesrv/glm.tar.gz"
    # version = otp
    version = "0.0.1"
    check_env(version, url)
    os.chdir(ProjectDir)
    sys.path.append(".")
    import main
    main.main(serial, label, otp, float(money))
