from fabric.api import *
from fabric.contrib import files
from fabric.contrib.files import exists, sed
from fabric.colors import green, red, blue
from fabric.contrib import project
import time
import json
import os
import zipfile
import sys
import pprint
import re

# env.use_ssh_config = False
# env.disable_known_hosts = True
# https://micropyramid.com/blog/automate-django-deployments-with-fabfile/

if os.name == 'nt':
    p = 'python'
else:
    p = 'python3'

try:
    with open("secret.json") as secret_file:
        secret = json.load(secret_file)
        env.update(secret)
        # env.hosts = secret['hosts']
except FileNotFoundError:
    print('***ERROR: no secret file***')

CWD = os.getcwd()
COMPONENTS_FOLDER = os.path.join(CWD, 'mainapp', 'templates', 'mainapp', 'components')
REMOTE_COMPONENTS_FOLDER = 'mainapp/templates/mainapp/components'

#check if WORKING_LOCAL is set to True
# r=root, d=directories, f = files
# for r, d, f in os.walk(CWD):
#     for file in f:
#         if file == 'settings.py':
#             path_to_settings = os.path.join(r, file)
#             with open(path_to_settings, 'r') as settings_file:
#                 for line in settings_file.readlines():
#                     if line.startswith('WORKING_LOCAL'):
#                         working_local_variable = [var.strip() for var in line.split('=')]
#                         if working_local_variable[1] == 'False':
#                             print(green('ERROR: SET WORKING LOCAL TO TRUE'))
#                             sys.exit()
try:
    with open("project.json") as project_file:
        project_data = json.load(project_file)
        pattern = re.compile('[^a-z0-9_]')
        if re.match(pattern, project_data['project_name']) or len(project_data['project_name']) == 0:
            print('ERROR PROJECT_NAME, sys.exit()')
            sys.exit()
        else:
            env.update(project_data)
except FileNotFoundError:
    print('***ERROR: no project file***')

PATH_TO_PROJECT = '{}/{}'.format(env.path_to_projects, env.project_name)


#check if os is not windows
if os.name != 'nt':
    env.use_ssh_config = True
    env.hosts = ['server']

def test_connection():
    # get_secret()
    run('ls -la')
    run('uname -a')

def backup():
    print(green('pulling remote repo...'))
    local('git pull')
    print(green('adding all changes to repo...'))
    local('git add .')
    print(green("enter your comment:"))
    comment = input()
    local('git commit -m "{}"'.format(comment))
    print(green('pushing master...'))
    local('git push -u origin master')


def backup_lock_files():
    # path to components mainapp/templates/mainapp/components
    for r, d, f in os.walk(COMPONENTS_FOLDER):
        for file in f:
            if file == 'installed.lock':
                file_path = os.path.join(r, file)
                local('cp {file_path} {file_path}_backup'.format(file_path=file_path))


def update_project_name_in_lock_files():
    for r, d, f in os.walk(COMPONENTS_FOLDER):
        for file in f:
            if set(['installed.lock', 'installed.lock_backup']).issubset(os.listdir(r)) and file=='installed.lock':
                file_path = os.path.join(r, file)
                print('FILE_PATH', file_path)
                with open(file_path, 'r') as lock_file:
                    file_data = lock_file.read()
                updated_file_data = file_data.replace('acgh-site', env.project_name)
                updated_file_data_dict = json.loads(updated_file_data)
                # import pdb; pdb.set_trace()
                # pprint.pprint(updated_file_data)
                with open(file_path, 'w') as updated_lock_file:
                    updated_lock_file.write(json.dumps(updated_file_data_dict))

def restore_lock_files():
    for r, d, f in os.walk(COMPONENTS_FOLDER):
        for file in f:
            if set(['installed.lock', 'installed.lock_backup']).issubset(os.listdir(r)):
                local('rm {}'.format(os.path.join(r, 'installed.lock')))
                local('cp {} {}'.format(os.path.join(r, 'installed.lock_backup'), os.path.join(r, 'installed.lock')))
                local('rm {}'.format(os.path.join(r, 'installed.lock_backup')))

def upload_lock_files():
    backup_lock_files()
    update_project_name_in_lock_files()
    for r, d, f in os.walk(COMPONENTS_FOLDER):
        for file in f:
            if file == 'installed.lock' and exists('{path_to_project}'.format(
                path_to_project=PATH_TO_PROJECT)):
                with open(os.path.join(r, file), 'r', encoding='utf-8') as lock_file:
                    component_name = json.load(lock_file)['title']
                    if exists('{path_to_project}/{remote_components_folder}/{component_name}/installed.lock'.format(
                        path_to_project=PATH_TO_PROJECT,
                        remote_components_folder=REMOTE_COMPONENTS_FOLDER,
                        component_name=component_name
                    )):
                        run('rm {path_to_project}/{remote_components_folder}/{component_name}/installed.lock'.format(
                            path_to_project=PATH_TO_PROJECT,
                            remote_components_folder=REMOTE_COMPONENTS_FOLDER,
                            component_name=component_name
                        ))
                put('{}'.format(os.path.join(r, file)),
                    '{path_to_project}/{remote_components_folder}/{component_name}/'.format(
                    path_to_project=PATH_TO_PROJECT,
                    remote_components_folder=REMOTE_COMPONENTS_FOLDER,
                    component_name=component_name
                ))
    restore_lock_files()


def git_remove_lock_and_styles():
    output = local("git ls-files *.lock", capture=True)+local("git ls-files *variables.scss", capture=True)
    if len(output) == 0:
        print('lock not in repo')
        return
    local('git rm --cached *installed.lock')
    local('git rm --cached *variables.scss')
    local("sed -i 's/# installed.lock/installed.lock/g; \
        s/# _variables.scss/_variables.scss/g' .gitignore")
    local('git add .')
    local('git commit -m "remove lock files and scss variables from repo before update"')
    print('removed lock_files and styles')


def git_add_lock_files_and_styles():
    output = local("git ls-files *.lock", capture=True)+local("git ls-files *variables.scss", capture=True)
    for line in output.splitlines():
        if any(['lock' in line, 'variables' in line]):
            print('lock files in repo:', line)
            return
    local("sed -i 's/installed.lock/# installed.lock/g; \
    s/_variables.scss/# _variables.scss/g' .gitignore")
    local('git add .')
    local('git commit -m "add lock files in repo"')


def rebuild_components():
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            # run('pwd')
            run('{python} manage.py install_components'.format(python=p))
            run('deactivate')


@runs_once
def remote_migrate():
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            run('{} manage.py makemigrations --noinput'.format(p))
            run('{} manage.py migrate --noinput'.format(p))
            run('deactivate')
    print(green(
        """
        ***************************
        **REMOTE MIGRATE COMPLETE**
        ***************************
        """
    ))

def local_migrate():
    local('{} manage.py makemigrations'.format(p))
    local('{} manage.py migrate'.format(p))
    print(green(
        """
        **********************
        **MIGRATION COMPLETE**
        **********************
"""
    ))

def app_migrate(app):
        with cd('{}'.format(PATH_TO_PROJECT)):
            with prefix(env.activate):
                run('pwd')
                run('{} manage.py makemigrations {}'.format(p, app))
                run('{} manage.py migrate {}'.format(p, app))
                run('deactivate')
                print(green(
                    """
                    ****************************
                    ***Django App {} migrated***
                    ****************************
                    """.format(app)))
# def activate_virtualenv():

# def deactivate():

def create_superuser():
    put('secret.json', '{}/'.format(PATH_TO_PROJECT))
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            run('pwd')
            run('{} manage.py init_admin'.format(p))
            run('deactivate')
            print(green("""
                *******************
                *Superuser created*
                *******************
                """
            ))

def check_exists(filename):
    if files.exists(filename):
        print(green('YES {} exists!'.format(filename)))
        return True
    else:
        print(red('{} NOT exists!'.format(filename)))
        return False

def test_remote_folder():
    execute(check_exists, '{}'.format(PATH_TO_PROJECT))

def test():
    local('{} manage.py test'.format(p))
    print(green(
        """
        ********************
        **Testing complete**
        ********************
        """
    ))

#as user
def clone():
    print(green('CLONING...'))
    run('git clone {}'.format(env.git_repo))
    print(green(
        """
        ********************
        **CLONING COMPLETE**
        ********************
        """
    ))


#as user
def remote_update():
    with cd('{}'.format(PATH_TO_PROJECT)):
        output = run("git status")
        for line in output.splitlines():
            if any(['нечего коммитить' in line, 'nothing to commit' in line]):
                print('WORKING TREE CLEAN')
                run("git pull")
                return
        print(green('UPDATING...'))
        run('git add .')
        run('git commit -m "server commit {}"'.format(time.ctime()))
        run('git pull')
    print(green(
"""
********************
**UPDATE COMPLETE***
********************
"""
    ))

#as user
def make_configs():
    local("sed 's/PROJECT_NAME/{}/g; \
                s/DOMAIN_NAME/{}/g; \
                s/USERNAME/{}/g' \
            nginx_config_template > {}_nginx".format(
        env.project_name, env.domain_name, env.user, env.project_name))
    print(green('***NGINX CONFIG READY***'))
    local("sed 's/PROJECT_NAME/{}/g; \
                s/USERNAME/{}/g' \
            systemd_config_template > {}.service".format(
        env.project_name, env.user, env.project_name))
    print(green('***SYSTEMD CONFIG READY***'))
    print(green("""
************************
****CONFIGS CREATED*****
************************
    """))

#as sudo
def copy_nginx_config():
    print(green('checking nginx-configuration'))
    # put('{}_nginx'.format(env.project_name), '/etc/nginx/sites-available/{}_nginx'.format(env.project_name), use_sudo=True)
    if not exists('/etc/nginx/sites-available/{}_nginx'.format(env.project_name), use_sudo=True):
        put('{}_nginx'.format(env.project_name), '/home/{}/'.format(env.user))
        sudo('mv /home/{}/{}_nginx /etc/nginx/sites-available/'.format(env.user, env.project_name))
        sudo('nginx -t')
        sudo('ln -s /etc/nginx/sites-available/{}_nginx /etc/nginx/sites-enabled/'.format(env.project_name))
        sudo('nginx -s reload')
    else:
        print(red('nginx configuration for project {} exists'.format(env.project_name)))

def copy_systemd_config():
    print(green('checking systemd-configuration'))
    if not exists('/etc/systemd/system/{}.service'.format(env.project_name)):
        put('{}.service'.format(env.project_name), '/home/{}'.format(env.user))
        sudo('mv /home/{}/{}.service /etc/systemd/system/'.format(env.user, env.project_name))
        sudo('systemctl enable {}.service'.format(env.project_name))
        sudo('systemctl start {}.service'.format(env.project_name))
    else:
        print(red('systemd {}.service already exists'.format(env.project_name)))

def copy_configs():
    copy_nginx_config()
    copy_systemd_config()
    print(green(
"""
*************************************
**SYSTEMD AND NGINX CONFIG UPLOADED**
*************************************
"""
    ))

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
    print(green(
"""
********************
***FOLDER ZIPPED****
********************
"""
    ))

def deploy_static():
    local('{} manage.py collectstatic --noinput'.format(p))
    zipf = zipfile.ZipFile('collected_static.zip', 'w', zipfile.ZIP_DEFLATED)
    execute(zipdir, 'static_root/', zipf)
    zipf.close()
    put('collected_static.zip', '{}/'.format(PATH_TO_PROJECT))
    local('rm collected_static.zip')
    with cd(PATH_TO_PROJECT):
        run('unzip collected_static.zip')
        run('rm collected_static.zip')
        sudo('nginx -s reload')
    # sudo('service gunicorn restart')
    sudo('systemctl restart {}.service'.format(env.project_name))
    sudo('nginx -s reload')
    print(green("""
        ***********************
        *Static files uploaded*
        ***********************
    """))


def put_youtube_plugin():
    pass


def local_collectstatic():
    local('{python} manage.py collectstatic --noinput'.format(python=p))

def remote_collectstatic():
    # manage.py collectstatic --noinput
    # if exists('{path}/static_root/'.format(path=PATH_TO_PROJECT)):
        # import pdb; pdb.set_trace()
        # run('rm -rf {path}/static_root/'.format(path=PATH_TO_PROJECT))
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            run('{python} manage.py collectstatic --noinput'.format(
                python=p))
    sudo('systemctl restart {config}.service'.format(config=env.project_name))
    sudo('nginx -s reload')
    print(green(
            """
            *********************************
            **REMOTE COLLECTSTATIC COMPLETE**
            *********************************
            """
        ))



def remote_test():
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            run('{python} manage.py test --project-name={project_name}'.format(
                python=p,
                project_name=env.project_name))
    print(green(
        """
        ************************
        **REMOTE TEST COMPLETE**
        ************************
        """
    ))

def commit():
    local('git add .')
    local('git commit -m "commit {}"'.format(time.ctime()))
    print(green(
        """
        ********************
        **COMMIT COMPLETE***
        ********************
        """
    ))

def fill_db_with_demo_data():
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            run('{} manage.py fill_db'.format(p))
    print(green(
        """
        **********************
        **DEMO DATA COMPLETE**
        **********************
        """
    ))
# mainapp/management/commands/randomize_colors.py
def remote_randomize_colorschemes():
    with cd('{}'.format(PATH_TO_PROJECT)):
        with prefix(env.activate):
            run('{python} manage.py randomize_colors'.format(python=p))
            print(green(
        """
        ************************
        **COLORSCHEMES CREATED**
        ************************
        """
    ))

def rename_template_folder():
    run('mv {path_to_projects}/acgh-site/ {path_to_project}'.format(
        path_to_projects=env.path_to_projects,
        path_to_project=PATH_TO_PROJECT
        ))
    print(green(
        """
        ****************************
        **PROJECT FOLDER RENAMED****
        ****************************
        """
    ))

def switch_debug_and_hosts():
    settings_path = '{path}/ac_site/settings.py'.format(path=PATH_TO_PROJECT)
    # domain_arr = env.domain_name.split('.')
    # import pdb; pdb.set_trace()
    # domain_escaped = "\\".join
    run(sed(settings_path, "DEBUG = True", "DEBUG = False"))
    run(sed(settings_path,
        'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = ["{}"]'.format(env.domain_name)
        ))
    #check if WORKING_LOCAL is set to True
    # r=root, d=directories, f = files
    # for r, d, f in os.walk(CWD):
    #     for file in f:
    #         if file == 'settings.py':
    #             path_to_settings = os.path.join(r, file)
    #             with open(path_to_settings, 'r') as settings_file:
    #                 for line in settings_file.readlines():
    #                     if line.startswith('WORKING_LOCAL'):
    #                         working_local_variable = [var.strip() for var in line.split('=')]
    #                         if working_local_variable[1] == 'False':
    #                             print(green('ERROR: SET WORKING LOCAL TO TRUE'))
    #                             sys.exit()


def clean():
    are_you_sure = prompt(red('ARE YOU SURE YOU WANT TO CLEAN? y/n:'))
    if are_you_sure == 'y':
        if exists(PATH_TO_PROJECT) and \
        exists('/etc/nginx/sites-available/{}_nginx'.format(env.project_name)) and \
        exists('/etc/nginx/sites-enabled/{}_nginx'.format(env.project_name)) and \
        exists('/etc/systemd/system/{}.service'.format(env.project_name)):
            try:
                sudo('rm -rf {}/'.format(env.project_name))
                sudo('rm /etc/nginx/sites-available/{}_nginx'.format(env.project_name))
                sudo('rm /etc/nginx/sites-enabled/{}_nginx'.format(env.project_name))
                sudo('systemctl stop {}.service'.format(env.project_name))
                sudo('rm /etc/systemd/system/{}.service'.format(env.project_name))
                sudo('nginx -s reload')
                local('rm {}_nginx'.format(env.project_name))
                local('rm {}.service'.format(env.project_name))
                print(green('***PROJECT_CLEANED***'))
            except Exception as e:
                print(red('ERROR: ', e))
        else:
            print(green('***PROJECT DOES NOT EXIST***'))
    else:
        print(green('***CLEANING CANCELED***'))


def wait(seconds):
    for i in range(seconds):
        left_seconds = seconds - i
        print(blue('...waiting {} seconds ...'.format(left_seconds)))
        time.sleep(1)


def local_push():
    output = local("git status", capture=True)
    for line in output.splitlines():
        if any(['нечего коммитить' in line, 'nothing to commit' in line]):
            print('WORKING TREE CLEAN')
            return
    local('git commit -a -m "fabric deploy"')
    local('git push -u origin master')


def change_project_name():
    print('project name', env.project_name)


def server_commit():
    print('commiting server changes')
    with cd('{}'.format(PATH_TO_PROJECT)):
        output = run("git status")
        for line in output.splitlines():
            if any(['нечего коммитить' in line, 'nothing to commit' in line]):
                print('WORKING TREE CLEAN')
                return
        print(green('COMMITING...'))
        run('git add .')
        run('git commit -m "server commit after update {}"'.format(time.ctime()))
    print(green(
"""
***************************
**SERVER COMMIT COMPLETE***
***************************
"""
    ))



def deploy():
    if not exists('{path_to_project}'.format(path_to_project=PATH_TO_PROJECT)):
        print(green('***Project folder {} does not exist***'.format(PATH_TO_PROJECT)))
        confirm = prompt(green('Start new deployment? ---> (y/n): '))
        if confirm == 'y':
            print(blue("""
                ************************
                STARTING in 3 seconds...
                ************************
            """))
            wait(3)
            git_add_lock_files_and_styles()
            test()
            local_push()
            clone()
            rename_template_folder()
            remote_migrate()
            create_superuser()
            app_migrate('mainapp')
            upload_lock_files()
            rebuild_components()
            fill_db_with_demo_data()
            make_configs()
            copy_systemd_config()
            copy_nginx_config()
            # deploy_static()
            # remote_test()
            remote_collectstatic()
            # change secret key
            # change debug mode
            # change allowed hosts
            # switch_debug_and_hosts()
            local('{} functional_tests.py {}'.format(p, env.domain_name))
            remote_collectstatic()
            print(blue("""
                *********************
                DEPLOYMENT COMPLETE...
                *********************
            """))
        else:
            print(green('***NEW DEPLOYMENT CANCELLED***'))
    else:
        print(green('...Project folder exists...'))
        confirm = prompt("Update? your answer y/n:")
        if confirm == 'y':
            test()
            git_remove_lock_and_styles()
            local_push()
            server_commit()
            remote_update()
            # upload_lock_files()
            # rebuild_components()
            remote_migrate()
            app_migrate('mainapp')
            remote_test()
            local('{} functional_tests.py {}'.format(p, env.domain_name))
            remote_collectstatic()
            # deploy_static()
            # change  secret_key
            # change debug mode
            # change allowed hosts
            server_commit()
            sudo('systemctl restart {}.service'.format(env.project_name))
            sudo('systemctl show {}.service --no-page'.format(env.project_name))
            sudo('nginx -s reload')
        else:
            print(green('***UPDATE CANCELLED***'))
