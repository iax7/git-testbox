#!/usr/bin/python
__author__ = 'iax'

import os
import sys
try:
    import yaml
except ImportError:
    sys.exit("""You need PyYAML!\nRun: pip install pyyaml""")
try:
    import paramiko
except ImportError:
    sys.exit("""You need paramiko!\nRun: pip install paramiko""")
import subprocess
import getopt
import getpass
import socket
import time


class Colors:
    blk    ='\033[0;30m' # Black - Regular
    red    ='\033[0;31m' # Red
    grn    ='\033[0;32m' # Green
    ylw    ='\033[0;33m' # Yellow
    blu    ='\033[0;34m' # Blue
    pur    ='\033[0;35m' # Purple
    cyn    ='\033[0;36m' # Cyan
    wht    ='\033[0;37m' # White
    b_blk  ='\033[1;30m' # Black - Bold
    b_red  ='\033[1;31m' # Red
    b_grn  ='\033[1;32m' # Green
    b_ylw  ='\033[1;33m' # Yellow
    b_blu  ='\033[1;34m' # Blue
    b_pur  ='\033[1;35m' # Purple
    b_cyn  ='\033[1;36m' # Cyan
    b_whi  ='\033[1;37m' # White
    u_blk  ='\033[4;30m' # Black - Underline
    u_red  ='\033[4;31m' # Red
    u_grn  ='\033[4;32m' # Green
    u_ylw  ='\033[4;33m' # Yellow
    u_blu  ='\033[4;34m' # Blue
    u_pur  ='\033[4;35m' # Purple
    u_cyn  ='\033[4;36m' # Cyan
    u_wht  ='\033[4;37m' # White
    bg_blk ='\033[40m'   # Black - Background
    bg_red ='\033[41m'   # Red
    bg_grn ='\033[42m'   # Green
    bg_ylw ='\033[43m'   # Yellow
    bg_blu ='\033[44m'   # Blue
    bg_pur ='\033[45m'   # Purple
    bg_cyn ='\033[46m'   # Cyan
    bg_wht ='\033[47m'   # White
    # High Intensity backgrounds
    bg_Iblk = '\033[0;100m'   # Black
    bg_Ired = '\033[0;101m'   # Red
    bg_Igrn = '\033[0;102m'   # Green
    bg_Iylw = '\033[0;103m'   # Yellow
    bg_Iblu = '\033[0;104m'   # Blue
    bg_Ipur = '\033[0;105m'   # Purple
    bg_Icyn = '\033[0;106m'   # Cyan
    bg_Iwht = '\033[0;107m'   # White
    # High Intensity
    Iblk='\033[0;90m'       # Black
    Ired='\033[0;91m'       # Red
    Igrn='\033[0;92m'       # Green
    Iylw='\033[0;93m'       # Yellow
    Iblu='\033[0;94m'       # Blue
    Ipur='\033[0;95m'       # Purple
    Icyn='\033[0;96m'       # Cyan
    Iwht='\033[0;97m'       # White
    # Bold High Intensity
    b_Iblk ='\033[1;90m'      # Black
    b_Ired ='\033[1;91m'      # Red
    b_Igrn ='\033[1;92m'      # Green
    b_Iylw ='\033[1;93m'      # Yellow
    b_Iblu ='\033[1;94m'      # Blue
    b_Ipur ='\033[1;95m'      # Purple
    b_Icyn ='\033[1;96m'      # Cyan
    b_Iwht ='\033[1;97m'      # White
    #RESET
    RST     = '\033[0m'    # Text Reset
    #Defined
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN= '\033[92m'
    WHITE  = '\033[1m'
    YELLOW = '\033[1;33m'
    WARNING= '\033[93m'
    FAIL   = '\033[91m'

    @classmethod
    def print_err(cls, msg):
        print cls.b_red + msg + cls.RST

    @classmethod
    def print_title(cls, msg):
        print cls.bg_wht + cls.b_blk + msg + cls.RST

    @classmethod
    def print_step(cls, msg):
        print cls.b_blu + msg + cls.RST

    @classmethod
    def print_value(cls, msg, value):
        print cls.b_Igrn + msg + ': ' + cls.grn + value + cls.RST

home = os.path.expanduser('~')
conf_file = home + '/.testbox.conf'


class Config:
    """Contains the remote box link configuration"""

    def __init__(self):
        self.local_user = ''  #'iax'
        self.local_machine = ''  #'ubuntu'
        self.local_sshkey_name = 'nova.pem'
        self.local_repo_dir = ''
        self.remote_host_prefix = ''  #'fw'
        self.remote_host = ''  #'15.185.250.159'
        self.remote_user = ''  #'ubuntu'
        self.repo_name = 'CDK-infra'
        self.remote_repo_dir = '/opt/config/production/git'

    def is_valid(self):
        if (self.local_user == '' or
            self.local_machine == '' or
            self.remote_host == '' or
            self.remote_user == ''):
            return False
        else:
            return True

    @property
    def local_sshkey(self):
        return home + '/.ssh/' + self.local_sshkey_name

    @property
    def current_location(self):
        return self.local_user + '@' + self.local_machine

    @property
    def remote_location(self):
        return self.remote_user + '@' + self.remote_host

    @property
    def root_remote_location(self):
        return 'root@' + self.remote_host

    @property
    def root_work_dir(self):
        return '{0}/{1}'.format(self.remote_repo_dir,
                                self.repo_name)

    @property
    def remote_user_repodir(self):
        return '/home/{0}/git/{1}.git/'.format(self.remote_user,
                                               self.repo_name)

    #Contains Standard Names for created objects
    @property
    def local_branch(self):
        return 'testing-{0}'.format(self.remote_host_prefix)

    @property
    def local_remote(self):
        return 'remote-{0}'.format(self.remote_host_prefix)

    @property
    def remote_user_branch(self):
        return 'test-of-{0}'.format(self.local_user)

    @property
    def remote_user_remote(self): #TO VALIDaTE
        return 'remote-of-{0}'.format(self.local_user)

    @property
    def remote_main_branch(self):
        return 'branch-of-{0}'.format(self.local_user)

    @property
    def remote_main_remote(self): #Legacy was testing
        return 'remote-of-{0}'.format(self.local_user)


class Ssh:
    def __init__(self):
        try:
            self.ssh = paramiko.SSHClient()
            #self.ssh.load_system_host_keys()
            #self.ssh.connect('ssh.example.com')
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(conf.remote_host, username=conf.remote_user, key_filename=conf.local_sshkey)
            return None
        except:
            Colors.print_err('There was a problem connecting to server.')
            sys.exit(4)

    def send_task(self, command, folder=''):
        print '[{0}{1}{2}]$ {3}{4}{5}'.format(Colors.WHITE,
                                              conf.remote_location,
                                              Colors.RST,
                                              Colors.YELLOW,
                                              command,
                                              Colors.RST)
        if folder != '':
            command = 'cd {0} ; {1}'.format(folder, command)
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.close()
        output_lines = stdout.read().splitlines()
        for line in output_lines:
            print line
        errors = stderr.read()
        if errors:
            for line in errors.splitlines():
                if line != 'stdin: is not a tty':
                    print line
        if len(output_lines) > 0:
            result = output_lines[-1]
        else:
            result = None
        return result

    def send_task_repo(self, command):
        return self.send_task(command, conf.remote_user_repodir)

    def send_root_task(self, command, folder=''):
        print '[{0}{1}{6}{2}]$ {3}{4}{5}'.format(Colors.WHITE,
                                                 conf.root_remote_location,
                                                 Colors.RST,
                                                 Colors.YELLOW,
                                                 command,
                                                 Colors.RST,
                                                 Colors.OKGREEN + folder)
        if folder != '':
            command = 'cd {0} ; {1}'.format(folder, command)
        stdin, stdout, stderr = self.ssh.exec_command('sudo -i bash -c \'' + command + '\'')
        stdin.close()
        output_lines = stdout.read().splitlines()
        for line in output_lines:
            print line
        errors = stderr.read()
        if errors:
            for line in errors.splitlines():
                if line != 'stdin: is not a tty':
                    print line
        if len(output_lines) > 0:
            result = output_lines[-1]
        else:
            result = None
        return result

    def send_root_task_mainrepo(self, command):
        return self.send_root_task(command, conf.root_work_dir)

    def local_task(self, command):
        print '[{0}{1}{2}]$ {3}{4}{5}'.format(Colors.WHITE,
                                              conf.current_location,
                                              Colors.RST,
                                              Colors.YELLOW,
                                              command,
                                              Colors.RST)
        p = subprocess.Popen(command, shell=True,
                             stderr=subprocess.PIPE)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        out = p.returncode
        return out

    def local_task_output(self, command):
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        # wait for the process to terminate
        out, err = p.communicate()
        errcode = p.returncode
        if len(out) > 0:
            return out.splitlines()[-1], errcode
        elif len(err) > 0:
            return err.splitlines()[-1], errcode
        else:
            return '', errcode

    def close(self):
        self.ssh.close()


def show_help():
    print """Usage is {0} [options] --configure <user@ip>
         {0} [options] --send
         {0} [options] --remove
Where:
 - help                : This info
 - configure <user@ip> : Configure a box to become a testing environment. The IP is the public address of the eroplus to use.
                         By default, configure will push your current branch code to the remote box. If you need to get the remote code locally and test on it, use --ref remote.
                         NOTE: If another user has configured the repo to his test, it will warn you, and require your approval.
 - send                : Shortcut to git push (in your workstation) and git pull on the remote box.
 - remove              : Will remove local and remote branch. This is exactly the invert of configure.
                         !!! Warning !!! You need to merge your code to master branch first.

Options:
 --key <name>        : Key file name. Default: nova.pem
 --repo <name>       : Without this option, by default, it will select your current repo.
 --remote-path <DIR> : By default, the path owned by root, is /opt/config/production/git/ by convention (puppet references). You can change it.
                     If the DIR doesn't exist, it will be created.

This script helps to implement everything to create a test environment connected to a testing local branch.
It helps you to test some code controlled by git (limit data loss risk, and environment controlled.) on a remote kit.""".format('testbox.py')


def read_yaml():
    #Creates if doesn't exists
    doesExists = os.path.isfile(conf_file)
    if not doesExists:
        open(conf_file, 'a').close()
    #Open file for reading
    file = open(conf_file, 'r')
    data = yaml.load(file)
    file.close()
    return data


def write_conf():
    file = open(conf_file, 'w')
    yaml.dump(conf, file)
    file.close()
    return None


def check_config():
    if not conf.is_valid():
        print 'testbox is not configured, please configured first before use it.'
        sys.exit(3)


def configure(arg):
    Colors.print_title('CONFIGURATION -------------------------------------------')
    conf.local_user = getpass.getuser()
    conf.local_machine = socket.gethostname()

    splited = arg.split('@')
    conf.remote_user = splited[0]
    conf.remote_host = splited[1]

    connection = Ssh()

    toplevel, err = connection.local_task_output("git rev-parse --show-toplevel")
    toplevel = toplevel.split('/')
    conf.repo_name = toplevel[-1]
    Colors.print_value('Repo Name', conf.repo_name)
    Colors.print_value('Remote Dir', conf.remote_repo_dir)

    conf.local_repo_dir, err = connection.local_task_output('git rev-parse --show-toplevel')
    fqdn = connection.send_root_task('facter fqdn')
    conf.remote_host_prefix = str(fqdn.split('.')[1])

    code = connection.local_task('ssh-add -l | grep nova.pem')
    if code != 0:
        connection.local_task('ssh-add {}/.ssh/nova.pem'.format(home))

    connection.send_task('mkdir -p git ; git init --bare git/{0}.git'.format(conf.repo_name))
    Colors.print_step('Creating local branch...')
    connection.local_task('git remote add {0} {1}:git/{2}.git'.format(conf.local_remote,
                                                                      conf.remote_location,
                                                                      conf.repo_name))
    connection.local_task('git checkout -b {0}'.format(conf.local_branch))
    connection.local_task('git push {0} {1}:{2}'.format(conf.local_remote,
                                                        conf.local_branch,
                                                        conf.remote_user_branch))
    connection.local_task('git branch --set-upstream-to={0}/{1}'.format(conf.local_remote,
                                                                        conf.remote_user_branch))

    exist_dir = connection.send_root_task('cd {0}/{1}'.format(conf.remote_repo_dir,
                                                              conf.repo_name))
    if exist_dir != None:
        Colors.print_step('Creating target remote repository directory...')
        connection.send_root_task_mainrepo('mkdir -p {0}/{1}; git init {0}/{1}'.format(conf.remote_repo_dir,
                                                                                       conf.repo_name))

    Colors.print_step('Creating remote branch...')
    connection.send_root_task_mainrepo('git remote add {0} /home/{1}/git/{2}.git/'.format(conf.remote_main_remote,
                                                                                          conf.remote_user,
                                                                                          conf.repo_name))
    connection.send_root_task_mainrepo('git fetch {0}'.format(conf.remote_main_remote))

    check_remote_branch(connection)

    connection.close()
    write_conf()
    return None


def check_remote_branch(connection):
    Colors.print_step('Checking remote branch...')
    branch = connection.send_root_task_mainrepo('git rev-parse --abbrev-ref HEAD')
    if branch == 'master':
        connection.send_root_task_mainrepo('git stash -k -u')
        exists = connection.send_root_task_mainrepo('git branch | grep {0}'.format(conf.remote_user_branch))
        if not exists:
            connection.send_root_task_mainrepo('git checkout --track remotes/{0}/{1}'.format(conf.remote_main_remote,
                                                                                             conf.remote_user_branch))
        else:
            connection.send_root_task_mainrepo('git checkout {0}'.format(conf.remote_user_branch))
    elif branch == conf.remote_user_branch:
        connection.send_root_task_mainrepo('git pull {0} {1}'.format(conf.remote_main_remote,
                                                                     conf.remote_user_branch))
    else:
        Colors.print_err('Approval required: The remote repository {0} is enabled on branch {1}. You need to confirm that you want to move to own branch'.format(
            conf.repo_name,
            branch))
    return None


def send():
    connection = Ssh()
    Colors.print_title('SEND ')
    #connection.local_task('git add -A :/')
    #Colors.print_step('Added all changes to commit')
    msg = 'Anonymous commit ' + time.strftime("%Y/%m/%d %I:%M:%S")
    #connection.local_task('git commit -m "{0}"'.format(msg))

    Colors.print_step('Sending changes...')
    connection.local_task('git push {0} HEAD:{1}'.format(conf.local_remote,
                                                         conf.remote_user_branch))
    check_remote_branch(connection)
    connection.send_root_task_mainrepo('git reset --hard {0}/{1}'.format(conf.remote_main_remote,
                                                                         conf.remote_user_branch))
    connection.send_root_task_mainrepo('git clean -f')
    connection.send_root_task_mainrepo('git pull {0} {1}'.format(conf.remote_main_remote,
                                                                 conf.remote_user_branch))


def remove():
    connection = Ssh()
    Colors.print_title('REMOVE -------------------------------------------')
    Colors.print_step('Removing local branch...')
    connection.local_task('git checkout master')
    connection.local_task('git branch -D {}'.format(conf.local_branch))
    connection.local_task('git remote remove {0}'.format(conf.local_remote))
    Colors.print_step('Removing remote branch... The remote testing repo won\'t be removed to prevent other tester to loose their branch.')
    connection.send_root_task_mainrepo('git reset --hard HEAD')
    connection.send_root_task_mainrepo('git checkout master')
    connection.send_root_task_mainrepo('git stash pop')
    connection.send_root_task_mainrepo('git branch -D {0}'.format(conf.remote_user_branch)) #TODO:remote_main_branch
    connection.send_task_repo('git branch -D {0}'.format(conf.remote_user_branch))
    result = connection.send_task_repo('git branch | grep -i test-of-'.format(conf.remote_user_branch))
    if not result:
        connection.send_root_task_mainrepo('git remote rm {0}'.format(conf.remote_main_remote))
        Colors.print_step('git remote <testing> was deleted.')
    else:
        Colors.print_step('Note: On the remote server, I did not remove the git remote testing, which is used by others.')

    connection.close()
    return None

#TODO: Almost repeated function from Ssh class, refactor to avoid duplicates
def local_task(command, show=False):
    if show:
        print '[{0}{1}{2}]$ {3}{4}{5}'.format(Colors.WHITE,
                                              conf.current_location,
                                              Colors.RST,
                                              Colors.YELLOW,
                                              command,
                                              Colors.RST)
    p = subprocess.Popen(command, shell=True,
                         stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(1)
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()
    out = p.returncode
    return out

conf = Config()

code = local_task('git rev-parse --show-toplevel 2>/dev/null', False)
if code != 0:
    Colors.print_err('You are not in a git repository. Move to a Repo clone directory and retry')
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[1:],
                               "hsrc:",
                               ["help", "send", "remove", "configure=", "repo=", "remote-path=", "key="])
    if len(opts) < 1:
        show_help()
        sys.exit(1)
except getopt.GetoptError:
    show_help()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', "--help"):
        show_help()
        sys.exit()
    elif opt in "--key":
        conf = read_yaml()
        check_config()
        conf.local_sshkey_name = arg
    elif opt in "--repo":
        conf = read_yaml()
        check_config()
        conf.repo_name = arg
    elif opt in "--remote-path":
        conf = read_yaml()
        check_config()
        conf.remote_repo_dir = arg
    elif opt in ("-c", "--configure"):
        configure(arg)
        print """-----------------------------------------------------
{0}\nYou are now in a new testing branch. Every commits here are specifics to this branch. a git push will move your code to the remote kit.
On the server, as root, you can do a git pull from {1}/{2}. And test your code.

When you are done, you will be able to merge to the master branch or any other branch you would use. As your commits were for testing, you may need to merge all your commits to one. So, think to use 'git rebase -i' to merge your pending commits to few commits before git push (or git-push for git review)""".format(
            Colors.wht + 'DONE' + Colors.RST,
            Colors.grn + conf.remote_repo_dir + Colors.RST,
            Colors.grn + conf.repo_name + Colors.RST
        )
    elif opt in ("-s", "--send"):
        conf = read_yaml()
        check_config()
        send()
    elif opt in ("-r", "--remove"):
        conf = read_yaml()
        check_config()
        remove()