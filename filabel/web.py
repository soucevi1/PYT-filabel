"""
The web application module of filabel. Used to deploy on a public website and automatically label the PRs using GitHub webhooks.
"""

from flask import Flask
from flask import render_template
from flask import request
import json 
import hashlib
import hmac
import requests
from filabel.github import *
import os
import sys


"""
Main Flask app
"""
app = Flask(__name__)


def get_conf_files():
    """
    Get names of both of the configuration files from environment
        :returns: configurations files or False if something went wrong
        :rtype: dictionary, bool
    """
    ret_files = {'cred': '', 'label': ''}
    cvar = os.getenv('FILABEL_CONFIG')
    if cvar == None:
        False
    # Test if there are more conf files
    cvar = cvar.split(':')
    if len(cvar) != 2:
        return False
    
    for fn in cvar:
        if not os.path.isfile(fn):
            return False
        with open(fn) as f:
            config = configparser.ConfigParser()
            config.read_file(f)
            if config.has_section('github'):
                ret_files['cred'] = fn
            elif config.has_section('labels'):
                ret_files['label'] = fn   

    if (ret_files['cred'] == '') or (ret_files['label'] == ''):
        return False
    return ret_files



@app.route('/', methods=['GET'])
def show_main_page(s=None):
    """
    Show main HTML page as a response to GET request.
        :returns: Rendered HTML template
        :rtype: HTML
    """
    filenames = get_conf_files()
    if filenames == False:
        return '', 500
    r = ''
    with open(filenames['label']) as f:
        r = get_label_patterns(f)
        if r == False:
            r = {'X': 'No label configuration supplied!'}
    username = get_username(filenames['cred'], s)
    if username == False:
        username = 'Unable to get'
    return render_template('main.html', name=username, rules = r)


def get_username(conf, s=None):
    """
    Get username of the token's owner.
        :param conf: credentials configuration file
        :returns: username of the repository owner, False if something went wrong
        :rtype: string, bool
    """
    sesison = requests.Session()
    with open(conf) as f:
        session = create_session(f, s)
    if session == False:
        return False
    u = session.get('https://api.github.com/user')
    u_json = u.json()
    if 'login' not in u_json:
        return False
    return u_json['login']


@app.route('/', methods=['POST'])
def react_to_post():
    """
    React to POST method - find if it came from GitHub and if it was sent by the corrent event
        :returns: Status code depending on the success
        :rtype: int
    """
    payload_headers = request.headers
    if 'X-GitHub-Event' not in payload_headers:
        return
    payload_json = request.get_json()
    if payload_headers['X-GitHub-Event'] == 'ping':
        if handle_ping(payload_headers) == False:
            app.logger.info('ping fail')
            return '', 404
        return '', 200
    elif payload_headers['X-GitHub-Event'] == 'pull_request':
        if handle_pull_request(payload_headers, payload_json['pull_request']) == False:
            return '', 501
        return '', 200
    else:
        return '', 500


def handle_ping(headers):
    """
    Answer to the ping request
        :param headers: request headers
        :returns: True if the ping is OK, False otherwise
        :rtype: bool
    """
    if check_signature(headers) == False:
        return False
    return True


def handle_pull_request(headers, pj):
    """
    Answer to the pull request request and change the labels
        :param headers: request headers
        :param pj: json file from GitHub
        :type headers: request.headers
        :type pj: JSON
        :returns: True if pull request was handled correctly, False otherwise
        :rtype: bool
    """
    if check_signature(headers) == False:
        return False
    filenames = get_conf_files()
    if filenames == False:
        print('Unable to get config files', file=sys.stderr)
        return False
    session = requests.Session()
    with open(filenames['cred']) as f:
        s = create_session(f)
        if s == False:
            print('Unable to open session', file=sys.stderr)
            return False
        session = s
    repo_name = get_repo_name(pj)
    if repo_name == False:
        return False
    pull_num = pj['number']
    labels_current = get_current_labels(pj['labels'])
    pull_filenames = get_pr_files(repo_name, session, pull_num)
    if pull_filenames == False:
        print(f'Unable to get the list of filenames of repo: {repo_name}, pull number: {pull_num}', file=sys.stderr)
        return False
    fpatterns = {}
    with open(filenames['label']) as f:
        fpatterns = get_label_patterns(f)
        if fpatterns == False:
            print('Unable to get list of patterns', file=sys.stderr)
            return False
    labels_new = get_all_labels(pull_filenames, fpatterns) 
    u_labels_to_keep = get_unknown_labels_to_keep(labels_current, fpatterns)
    labels_to_add = labels_new
    labels_to_add += u_labels_to_keep
    labels_to_add = list(set(labels_to_add))
    fl = add_labels(repo_name, pull_num, labels_to_add, session)     
    if fl == False:
        print('Unable to add labels', file=sys.stderr)
        return False
    return True


    
def get_repo_name(p_json):
    """
    Get name of the current repository
        :param p_json: json of the pull request
        :type p_json: JSON
        :returns: Name of the current repository
        :rtype: string
    """
    if 'base' not in p_json:
        print('No "base" in pull request payload', file=sys.stderr)
        return False
    if 'repo' not in p_json['base']:
        print('No "repo" in pull request payload', file=sys.stderr)
        return False
    if 'full_name' not in p_json['base']['repo']:
        print('No "full_name" in pull request payload', file=sys.stderr)
        return False
    return p_json['base']['repo']['full_name']



def check_signature(headers, d=None):
    """
    Verify the X-Hub-Signature
        :param headers: request headers
        :type headers: request.headers
        :returns: True if the signature is OK, False otherwise
        :rtype: bool
    """
    secret = get_secret()
    if secret == False:
        return False
    if 'X-Hub-Signature' not in headers:
        print('no signature')
        return False
    sig = headers['X-Hub-Signature']
    sha_name, signature = sig.split('=')
    if sha_name != 'sha1':
        print('wrong hashfunction')
        return False
    s = bytearray(secret, 'utf8')
    m = d or request.data
    h = hmac.new(s, msg=m, digestmod=hashlib.sha1)
    my_signature = h.hexdigest()
    if hmac.compare_digest(my_signature, signature) == False:
        print(f'secret: {s}\nmsg: {m}\nsig: {signature}\nmy: {my_signature}', file=sys.stderr)
        return False     
    return True


def get_secret():
    """
    Read the webhook secret from configuration file
        :returns: GitHub webhook secret
        :rtype: string
    """
    conf_files = get_conf_files()
    if conf_files == False:
        return False
    config = configparser.ConfigParser()
    ret = False
    with open(conf_files['cred']) as f:
        config.read_file(f)
        if config.has_section('github') == False:
            return False
        opts = config.options('github')
        for o in opts:
            if o == 'secret':
                ret = config.get('github', o)
    return ret

