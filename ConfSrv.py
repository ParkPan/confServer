import webService
import yaml
import os


class ConfMrg(object):

    def __init__(self):
        self.srv_role_info = {}
        self.conf_role_info = {}

    def load_srv_confile(self, pathfile):
        try:
            fhandler = open(pathfile)
            self.srv_role_info = yaml.load(fhandler)
        finally:
            if fhandler is not None:
                fhandler.close()

    def load_cof_confile(self, pathfile):
        try:
            fhandler = open(pathfile)
            self.conf_role_info = yaml.load(fhandler)
        finally:
            if fhandler is not None:
                fhandler.close()

    def set_srv_confile(self, pathfile):
        try:
            fhandler = open(pathfile, "w")
            fhandler.write(yaml.dump(self.srv_role_info))
            fhandler.flush()
        finally:
            if fhandler is not None:
                fhandler.close()

    def get_file_list(self, rootpath, role, verfolder):
        filelist = []
        folderlist = []
        if role not in self.conf_role_info:
            return None, None
        rolepath = self.conf_role_info[role]["rootpath"]
        filespath = os.path.join(rootpath, rolepath)
        _, tmpfds, _ = os.walk(filespath).next()
        ver_adapter = self.get_adapte_version(verfolder, tmpfds)
        filespath = os.path.join(filespath, ver_adapter)
        for root, folders, files in os.walk(filespath):
            for tmpfile in files:
                executable = False
                if os.access(tmpfile, os.X_OK):
                    executable = True
                filelist.append((os.path.join(root, tmpfile), executable))
            for tmpfolder in folders:
                folderlist.append(os.path.join(root, tmpfolder))
        ret_folder_list = [item.replace(filespath+os.path.sep, "") for item in folderlist]
        ret_file_list = [(item[0].replace(filespath+os.path.sep, ""), item[1]) for item in filelist]
        return ver_adapter, ret_folder_list, ret_file_list

    def get_adapte_version(self, ver_adapte, ver_collection):
        ret_ver = ver_adapte
        if ver_adapte == "latest":
            return ret_ver
        else:
            tmpindex = ver_collection.index("latest")
            del ver_collection[tmpindex]
            if len(ver_collection) == 0:
                return "latest"
            ver_collection.sort(reverse=True)
            if ver_adapte > ver_collection[0]:
                return "latest"
            else:
                for i in range(len(ver_collection)):
                    if ver_adapte > ver_collection[i]:
                        ret_ver = ver_collection[i - 1]
                        break
                else:
                    ret_ver = ver_collection[len(ver_collection) - 1]
        return ret_ver

    def get_file_params(self, role, verfolder):
        if "variables" in self.conf_role_info[role]:
            ver_adapter = self.get_adapte_version(verfolder, self.conf_role_info[role]["variables"].keys())
            return self.conf_role_info[role]["variables"][ver_adapter]
        else:
            return None


__conf_mrg = None


def get_conf_mrg():
    global __conf_mrg
    if __conf_mrg is None:
        __conf_mrg = ConfMrg()
        __conf_mrg.load_srv_confile("./serverinfo.yml")
        __conf_mrg.load_cof_confile("./confinfo.yml")
    return __conf_mrg


def start_server(port):
    webService.start_service(port)


if __name__ == "__main__":
    start_server(12021)
    # get_conf_mrg()
