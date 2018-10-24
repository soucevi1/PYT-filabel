import requests
import json
import fnmatch
import configparser


token = 'abc'


def token_auth(req):
    """Helper function for the session"""
    req.headers['Authorization'] = f'token {token}'
    return req


def get_auth(f):
    """Get authentication token from config file"""
    config = configparser.ConfigParser()
    config.read_file(f)
    if config.has_section('github') == False:
        return False
    opts = config.options('github')
    ret = ''
    for o in opts:
        if o == 'token':
            ret = config.get('github', o)
    if ret == '':
        return False
    return ret


def create_session(config_auth):
    """Create session using the access token"""
    global token
    token = get_auth(config_auth)
    if token == False:
        return False
    session = requests.Session()
    session.headers = {'User-Agent': 'soucevi1'}
    session.auth = token_auth
    return session



def get_pr_files(r, session, pull_num):
    """
    Get list containing all the files that are modified in the current pull request
        r: string 'author/repo-name'
        session: open and authenticated session
        pull_num: number of the pull request
    """
    pull_files = session.get(f'https://api.github.com/repos/{r}/pulls/{pull_num}/files')
    if pull_files.status_code != 200:
        print(f'Response code: {pull_files.status_code} from https://api.github.com/repos/{r}/pulls/{pull_num}/files', file=sys.stderr)
        return False
    flist = get_pr_filenames(pull_files.json())

    lasturl = 'abc'
    if 'Link' not in pull_files.headers:
        return flist

    while True:
        links = requests.utils.parse_header_links(pull_files.headers['Link'])
        n_flag = False
        for l in links:
            if l['rel'] == 'next':
                pull_files = session.get(l['url'])
                if pull_files.status_code != 200:
                    print(f'Response code: {pull_files.status_code} from https://api.github.com/repos/{r}/pulls/{pull_num}/files', file=sys.stderr)
                    return False
                n_flag = True
                break
        flist += get_pr_filenames(pull_files.json())
        if n_flag == False:
            break        
    return flist



def get_pr_filenames(fj):
    """
    Parse filenames from file json
        fj: files json
    """
    fns = []
    for i in range(len(fj)):
        fns.append(fj[i]['filename'])
    return fns



def get_all_labels(filenames, pattern_dict):
    """
    Get labels to add to the PR
        filenames: list of fns
        paterns: dict "label:[pattern, p...]"
    """
    ret = []
    for fn in filenames:
        for entry in pattern_dict:
            for i in range(len(pattern_dict[entry])):
                if (fnmatch.fnmatch(fn, pattern_dict[entry][i])) and (entry not in ret):
                    ret.append(entry)              
    return ret



def get_label_patterns(file):
    """
    Parse fn patterns from config file
    """
    config = configparser.ConfigParser()
    config.read_file(file)
    if config.has_section('labels') == False:
        return False
    opts = config.options('labels')
    ret = {}
    for o in opts:
        patterns = config.get('labels', o)
        patts = patterns.split('\n')
        if '' in patts:
            patts.remove('')
        ret[o] = patts
    return ret


def get_unknown_labels_to_keep(labels_curr, pattern_dict):
    """
    Filter out the labels that match the configuration file
    """
    ret = []
    pat = []
    for entry in pattern_dict:
        pat.append(entry)
    for l in labels_curr:
        if l in pat:
            continue
        else:
            ret.append(l)
    return ret



def add_labels(repo, pull_num, labels, session):
    """
    Add all the labels to the PR
    """
    params = json.dumps(labels)
    ret = session.put(f'https://api.github.com/repos/{repo}/issues/{pull_num}/labels', 
        data=params)
    if ret.status_code != 200:
        return False
    if test_labels_added(repo, pull_num, labels, session) == False:
        return False
    return True



def get_current_labels(lj):
    """
    Get labels from json file
    """
    ret = []
    for i in lj:
        ret.append(i['name'])
    return ret


def test_labels_added(repo, pull_num, labels, session):
    """
    Test whether the labels were added correctly (permissions etc.)
    """
    ret = session.get(f'https://api.github.com/repos/{repo}/issues/{pull_num}/labels')
    if ret.status_code != 200:
        return False

    llist = get_label_names(ret.json())

    if 'Link' in ret.headers:
        while True:
            links = requests.utils.parse_header_links(ret.headers['Link'])
            n_flag = False
            for l in links:
                if l['rel'] == 'next':
                    ret = session.get(l['url'])
                    if ret.status_code != 200:
                        return False
                    n_flag = True
                    break
            llist += get_label_names(ret.json())
            if n_flag == False:
                break    
    if set(llist) != set(labels):
        return False
    return True


def get_label_names(l_json):
    """
    Get names of all the labels in given json
    """
    llist = []
    for j in l_json:
        llist.append(j['name'])
    return llist
