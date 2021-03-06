"""
Very simple deploy script that assumes a lot of existing setup
"""

from fabric.api import *

code_path = '/home/ubuntu/tapmapper/tapmapper'


def pull():
    with cd(code_path):
        run('git fetch')
        run('git reset --hard origin/master')


def install():
    with cd(code_path):
        sudo('pip install -r requirements.txt')
        sudo('pip install -e .')


def serve():
    run('supervisorctl restart all')


def deploy():
    pull()
    install()
    serve()
