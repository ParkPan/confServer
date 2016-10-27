import tornado
import tornado.web
import os
import ConfSrv
import json
import error
import thread


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, mrg):
        self.cofMrg = mrg

    def get(self):
        self.cofMrg.load_srv_confile("./serverinfo.yml")
        self.render("index.html", serverinfo=self.cofMrg.srv_role_info)

# ---------------- for jenkins -- index_add.html ----------------------
#class MainHandler(tornado.web.RequestHandler):
#    def get(self):
#        # self.write("Hello, world")
#        # os.walk()
#        server = jenkins.Jenkins('http://192.168.5.129:8080')
#        jobs = server.get_jobs()
#        tmpitems = []
#        for job in jobs:
#            tmpitems.append(job['name'])
#        self.render('index.html', items=tmpitems)

#class BuildDeploy(tornado.web.RequestHandler):
#    def post(self):
#        # self.deploy_package('apache-flume-1.6.0-bin.tar.gz', '/home/admin/testtar', '10.103.0.6')
#        project_name = self.get_argument("list", None)
#        remote_ip = self.get_argument("remote_ip", None)
#        remote_path = self.get_argument("remote_path", None)
#        package_name = self.get_argument("package_name", None)
#        if project_name:
#            # server = jenkins.Jenkins('http://192.168.5.129:8080')
#            # # user = server.get_whoami()
#            # # version = server.get_version()
#            # # print('Hello %s from Jenkins %s' % (user['fullName'], version))
#            # # build_number_old = server.get_job_info(project_name)['lastBuild']['number']
#            # build_number_next = server.get_job_info(project_name)['nextBuildNumber']
#            # print build_number_next
#            # server.build_job(project_name)
#            # time.sleep(10)
#            # # info = server.get_job_info(project_name)
#            # # print server.get_build_info(project_name, build_number_next)['building']
#            # while server.get_build_info(project_name, build_number_next)['building']:
#            #     time.sleep(10)
#            #     print 'waiting building finish...'
#            # build_number = server.get_job_info(project_name)['lastCompletedBuild']['number']
#            # if build_number_next != build_number or server.get_build_info(project_name, build_number)['result'] != 'SUCCESS':
#            #     # build_info = server.get_build_info(project_name, build_number)
#            #     # print 'in if ...'
#            #     self.write('create build job failed...')
#            # else:
#            #     # print 'out if ...'
#            #     # print build_number, build_number_next, server.get_build_info(project_name, build_number)['result']
#            #     # build_info = server.get_job_info(project_name)
#            #     # print build_info
#                src_path = jenkins_dir + r'%s/workspace/%s/'%(project_name, project_name)
#                self.copy_package(src_path, remote_path, package_name, remote_ip, '192.168.5.129')
#                self.deploy_package(package_name, remote_path, remote_ip)
#        else:
#            resp = 'no project name parameter in request url'
#            self.write(resp)
#
#    def copy_package(self, src_path, des_path, package_name, des_ip, src_ip):
#        ssh_shell = pexpect.spawn('scp admin@%s:%s admin@%s:%s' % (src_ip, os.path.join(src_path, package_name), des_ip, des_path))
#        # ssh_shell = pexpect.spawn('scp admin@%s:%s test@%s:%s' % (src_ip, jenkins_dir, des_ip, '~'))
#        match_index = ssh_shell.expect(['continue connecting (yes/no)', 'password:', pexpect.TIMEOUT], timeout=2)
#        if match_index == 0:
#            ssh_shell.sendline('yes')
#            ssh_shell.expect('password:', timeout=2)
#            ssh_shell.sendline('xxxxxx')
#        elif match_index == 1:
#            ssh_shell.sendline('xxxxxx')
#        else:
#            ssh_shell.sendcontrol('c')
#            ssh_shell.close()
#            return 'execute scp command failed, cannot copy build package to destination server ...'
#
#        ssh_shell.expect('password:', timeout=2)
#        ssh_shell.sendline('xxxxxx')
#        ssh_shell.expect(pexpect.EOF)
#        ssh_shell.close()
#        # ssh_shell.interact()
#
#    def deploy_package(self, package_name, target_path, target_ip):
#        ssh_shell = pexpect.spawn('ssh admin@%s' % target_ip)
#        match_index = ssh_shell.expect(['password', pexpect.TIMEOUT], timeout=30)
#        if match_index == 0:
#            ssh_shell.sendline('xxxxxx')
#        else:
#            ssh_shell.sendcontrol('c')
#            ssh_shell.close()
#            return 'execute scp command failed, cannot copy build package to destination server ...'
#        ssh_shell.expect('$')
#        ssh_shell.sendline('cd %s' % target_path)
#        ssh_shell.expect('$')
#        ssh_shell.sendline('pwd')
#        match_index = ssh_shell.expect(['%s' % target_path, pexpect.TIMEOUT], timeout=2)
#        if match_index == 0:
#            ssh_shell.sendline('tar -xzvf %s' % package_name)
#            ssh_shell.expect('$')
#            ssh_shell.sendline('cd %s' % package_name)
#            ssh_shell.expect('$')
#            ssh_shell.sendline('exit')  # can start app etc ...
#            ssh_shell.expect(pexpect.EOF)
#            ssh_shell.close()
#        else:
#            ssh_shell.sendcontrol('c')
#            ssh_shell.close()
#            return 'cannot in expect dir, shell exit ...'#
# ---------------------------------------------------------------------

class DownloadFile(tornado.web.RequestHandler):
    def initialize(self, mrg):
        self.cofMrg = mrg

    def get(self):
        role = self.get_argument("role",None)
        ip = self.get_argument("ip",None)
        filepath = self.get_argument("filepath",None)
        hostname = self.get_argument("hostname", None)
        verfolder = self.get_argument("verfolder", None)
        if not role or not filepath or not verfolder:
            return self.write(error.pack_errinfo_json(error.ERROR_PARAM_ARG_MISSING,"role or filepath or version-folder"))
        params = self.cofMrg.get_file_params(role, verfolder)
        if params is None:
            params = {}
        params["remote_ip"] = ip
        params["remote_hostname"] = hostname
        rolepath = self.cofMrg.conf_role_info[role]["rootpath"]
        rolepath = os.path.join(rolepath, verfolder)
        loader = tornado.template.Loader("./templates/conf/" + rolepath)
        relative_fulle_filepath = "./templates/conf/" + rolepath + "/" + filepath
        if not os.path.exists(relative_fulle_filepath):
            resp = error.pack_errinfo_json(error.ERROR_PARAM_INVALID_PARAMETER,"filepath")
        else:
            resp = loader.load(filepath).generate(params=params)
        self.write(resp)


class FileList(tornado.web.RequestHandler):
    def initialize(self, mrg):
        self.cofMrg = mrg

    def get(self):
        role = self.get_argument("role", None)
        verfolder = self.get_argument("verfolder", None)
        if not role or not verfolder:
            return self.write(error.pack_errinfo_json(error.ERROR_PARAM_ARG_MISSING,"role or version-folder"))
        ip = self.request.headers.get("X-Real-IP") or self.request.remote_ip
        if not ip:
            return self.write(error.pack_errinfo_json(error.ERROR_INTERNAL_SERVER_ERROR,"can't fecth remote_ip"))
        version, folders, files = self.cofMrg.get_file_list(r"./templates/conf", role, verfolder)
        if not files and not folders:
            return self.write(error.pack_errinfo_json(error.ERROR_PARAM_INVALID_PARAMETER,"role"))
        file_segs = [{"filepath":item[0], "executable":item[1]} for item in files]
        content = {"folders":folders,"files":file_segs,"ip":ip, "version": version}
        resp = json.dumps(content)
        self.write(resp)


class CollectVersion(tornado.web.RequestHandler):
    def initialize(self, mrg):
        self.cofMrg = mrg

    def post(self):
        version_str = self.request.body
        josn_str = json.loads(version_str)
        role = josn_str["role"]
        if not role:
            return self.write(error.pack_errinfo_json(error.ERROR_PARAM_ARG_MISSING,"role"))
        ip = self.request.headers.get("X-Real-IP") or self.request.remote_ip
        if not ip:
            return self.write(error.pack_errinfo_json(error.ERROR_INTERNAL_SERVER_ERROR,"can't fecth remote_ip"))
        # ip = "0.0.0.0"
        new_list = ["lasted"]
        new_list.extend([item.encode("ascii") for item in josn_str["versions"]])
        for item in self.cofMrg.srv_role_info[role]:
            if ip in item:
                item[ip] = new_list
                break
        else:
            return self.write(json.dumps({}))
        self.cofMrg.set_srv_confile("./serverinfo.yml")
        self.write(json.dumps({}))


class UploadFile(tornado.web.RequestHandler):
    def initialize(self, mrg):
        self.cofMrg = mrg

    def post(self):
        upload_info = self.request.body
        # info_obj = json.dumps(upload_info)
        info_obj = json.loads(upload_info)
        thread.start_new_thread(UploadFile.create_file_work, (info_obj,))
        self.write("ok finish")

    @staticmethod
    def create_file_work(info_obj):
        root_path = "./templates/backup"
        role = info_obj["role"]
        root_folder = os.path.join(root_path, role)
        up_folder = info_obj["upfolder"]
        full_folder = os.path.join(root_folder, up_folder.replace(os.path.sep, ""))
        up_file = info_obj["upfile"]
        up_body = info_obj["upbody"]
        if not os.path.exists(full_folder):
            os.makedirs(full_folder)
        full_file = os.path.join(full_folder, up_file)
        with open(full_file, "w") as fd:
            fd.write(up_body)
        # if executable:
        #     old_mode = os.stat(full_relatve_filepath).st_mode
        #     os.chmod(full_relatve_filepath, old_mode | stat.S_IXUSR)


def start_service(port):
    __cofMrg = ConfSrv.get_conf_mrg()
    application = tornado.web.Application([
        # (r"^/static/(.*)",tornado.web.StaticFileHandler,{"path":"./statics/"}),
        (r"/", MainHandler, dict(mrg=__cofMrg)),
        (r"/download", DownloadFile, dict(mrg=__cofMrg)),
        (r"/filelist", FileList, dict(mrg=__cofMrg)),
        (r"/collectversion", CollectVersion, dict(mrg=__cofMrg)),
        (r"/uploadfile", UploadFile, dict(mrg=__cofMrg)),
        #(r"/builddeploy", BuildDeploy), # for add.html
        #(r"/ajaxtest", AjaxTest), # for add.html
    ], template_path=os.path.join(os.path.dirname(__file__), "templates"))
    application.listen(port)
    tornado.ioloop.IOLoop.current().start()
