import os
import tarfile, urllib.request, pathlib

ProjectDir = "/home/admin/env/glm"
OldProjectDir = f"{ProjectDir}_old"
TempProjectDir = "/home/admin/env/download/glm"
DownloadDir = "/home/admin/env/download"
TarFilename = "glm.tar.gz"

def install_tar_url(url: str):
    """下载 tar.gz"""

    cwd = os.getcwd()
    os.rmdir(DownloadDir)
    os.mkdir(DownloadDir)
    tar_path = pathlib.Path(DownloadDir) / "glm.tar.gz"
    print("Downloading", url)
    urllib.request.urlretrieve(url, tar_path)

    print("Extracting...")
    os.chdir(DownloadDir)
    with tarfile.open(tar_path, "r:gz") as tf:
        tf.extractall(DownloadDir)
    os.chdir(cwd)
    # 链接与清理
    os.remove(OldProjectDir)
    os.rename(OldProjectDir, ProjectDir)
    os.rename(ProjectDir, TempProjectDir)

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
