"""
Module containing the GitHub logic used in filabel.
"""

import requests
import json
import fnmatch
import configparser
import sys

"""
GitHub authorization token
"""
token = 'abc'


def token_auth(req):
    """
    Helper function for the GitHub session
    """
    req.headers['Authorization'] = f'token {token}'
    return req


def get_auth(f):
    """
    Get authentication token from config file
        :param f: configuration file with credentials
        :type f: file
        :returns: parsed GitHub token, False if something went wrong
        :rtype: string, bool
    """
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


def create_session(config_auth, s=None, t=None):
    """
    Create session using the access token
        :param config_auth: configuration file containing credentials
        :param s: debug param
        :param t: debug param
        :type config_auth: file
        :returns: open GitHub session, False if something went wrong
        :rtype: requests.Session(), bool
    """
    global token
    token = t or get_auth(config_auth)
    if token == False:
        return False
    session = s or requests.Session()
    session.headers = {'User-Agent': 'soucevi1'}
    session.auth = token_auth
    return session


def get_pr_files(r, session, pull_num):
    """
    Get list containing all the files that are modified in the current pull request
        :param r: string 'author/repo-name'
        :param session: open and authenticated session
        :param pull_num: number of the pull request
        :type r: string
        :type session: requests.Session()
        :type pull_num: int
        :returns: list of files contained in the pull requests
        :rtype: list
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
        if n_flag == False:
            break
        flist += get_pr_filenames(pull_files.json())        
    return flist



def get_pr_filenames(fj):
    """
    Parse filenames from file json
        :param fj: pull requests files JSON
        :type fj: JSON
        :returns: list of filenames from one pull request
        :rtype: list
    """
    fns = []
    for i in range(len(fj)):
        fns.append(fj[i]['filename'])
    return fns



def get_all_labels(filenames, pattern_dict):
    """
    Get labels to add to the PR
        :param filenames: list of filenams
        :param patern_dict: rules for labeling
        :type filnames: list
        :type pattern_dict: dictionary
        :returns: list of labels belonging to the pull request
        :rtype: list
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
    Parse filename patterns from config file
        :param file: configuration file containing labeling rules
        :type file: file
        :returns: parsed labeling rules, False if something went wrong
        :rtype: dictionary, bool
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
        :param labels_curr: known labels
        :param pattern_dict: dirtionary containing all the mach rules
        :type labels_curr: list
        :type pattern_dict: dictionary
        :returns: list of labels
        :rtype: list
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
        :param repo: repository
        :param pull_num: number of pull request
        :param labels: labels to add
        :param session: open Github session
        :type repo: string
        :type pull_num: int
        :type labels: list
        :type session: requests.Session
        :returns: True if labels added successfully, False otherwise
        :rtype: bool
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
        :param lj: labels JSON
        :type lj: JSON
        :returns: list of label names
        :rtype: list
    """
    ret = []
    for i in lj:
        ret.append(i['name'])
    return ret


def test_labels_added(repo, pull_num, labels, session):
    """
    Test whether the labels were added correctly (permissions etc.)
        :param repo: repository
        :param pull_num: number of pull request
        :param labels: labels that were added
        :param session: open github session
        :type repo: string
        :type pull_num: int
        :type labels: list
        :type session: requests.Session
        :returns: True if labels are correct, False oherwise
        :rtype: bool
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
        :param l_json: list of labels jsons
        :type l_json: list
        :returns: list of labels names
        :rtype: list
    """
    llist = []
    for j in l_json:
        llist.append(j['name'])
    return llist
