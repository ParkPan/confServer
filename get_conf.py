import shutil
import os
import urllib2
import urllib
import json
import stat
import socket
import re

role = "stun"
backup_path = r"F:\ttt"
# version = "lasted"


def get_conf_files_down():
    report_version_info()
    conf_path = "./conf"
    if os.path.exists(conf_path):
        shutil.rmtree(conf_path, ignore_errors=True)
    os.mkdir(conf_path)
    folders, files, ip, verfolder = get_remote_conf_info()
    hostname = socket.gethostname()
    if (not folders and not files) or not ip:
        print "failed to get remote configure info"
        return False
    try:
        for folder in folders:
            foler_path = os.path.join(conf_path, folder)
            os.makedirs(foler_path)
        for file_info in files:
            file, executable = file_info["filepath"], file_info["executable"]
            content = download(file, ip, hostname, verfolder)
            if not content:
                return False
            full_relatve_filepath = os.path.join(conf_path, file)
            with open(full_relatve_filepath, "w") as fd:
                fd.write(content)
            if executable:
                old_mode = os.stat(full_relatve_filepath).st_mode
                os.chmod(full_relatve_filepath, old_mode | stat.S_IXUSR)
        return True
    except Exception, e:
        print str(e)
        return False


def get_remote_conf_info():
    args = {"role":role, "verfolder": get_folder_version()}
    args = urllib.urlencode(args)
    url = "http://config.cloutropy.com:12021/filelist?%s" % args
    try:
        content = urllib2.urlopen(url).read()
        result = json.loads(content)
        if result.get("result") == "fail":
            print content
            return None, None, None, None
        return result.get("folders"), result.get("files"), result.get("ip"), result.get("version")
    except Exception, e:
        print str(e)
        return None, None, None, None


def download(filepath, ip, hostname, verfolder):
    args = {"role": role, "ip": ip, "filepath": filepath, "hostname": hostname, "verfolder": verfolder}
    args = urllib.urlencode(args)
    url = "http://config.cloutropy.com:12021/download?%s" % args
    try:
        content = urllib2.urlopen(url).read()
        return content
    except Exception, e:
        print str(e)
        return None


def report_version_info():
    _, folders, _ = os.walk(backup_path).next()
    jsonobj = {"role": role, "versions": folders}
    jsonstr = json.dumps(jsonobj,  ensure_ascii=False)
    url = "http://config.cloutropy.com:12021/collectversion?role=%s"%role
    req = urllib2.Request(url=url, data=jsonstr)
    urllib2.urlopen(req)


def get_conf_files(rootpath="./conf"):
    filelist = []
    root, folders, files = os.walk(rootpath).next()
    for tmpfile in files:
        filelist.append((root, tmpfile))
    for tmpfolder in folders:
        filelist.extend(get_conf_files(os.path.join(rootpath, tmpfolder)))
    return filelist


def upload_file(upfolder, upfile, rootpath="./conf"):
    # full_folder = os.path.join(rootpath, upfolder)
    full_file = os.path.join(upfolder, upfile)
    with open(full_file, "rb") as fd:
        content = fd.read()
    url = "http://config.cloutropy.com:12021/uploadfile"
    file_info_obj = {"role": role, "upfolder": upfolder.replace(rootpath, ""), "upfile": upfile, "upbody": content}
    file_info_str = json.dumps(file_info_obj)
    req = urllib2.Request(url=url, data=file_info_str)
    urllib2.urlopen(req)


def get_folder_version():
    abspath = os.path.abspath(os.path.dirname(__file__))
    _, folder_name = os.path.split(abspath)
    if folder_name.find(".") == -1:
        return "latest"
    version = folder_name.split(".")[len(folder_name.split(".")) - 1]
    m = re.match("\d{8}", version)
    if m:
        return m.group()
    else:
        return "latest"


if __name__ == "__main__":
    get_conf_files_down()
    # get_conf_files()
    # report_version_info()
    # flist = get_conf_files()
    # print len(flist)
    # print flist
    # for upfolder, upfile in flist:
    #     upload_file(upfolder, upfile)
    # print get_folder_version()
