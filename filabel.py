import click
import colorama
import configparser
import requests
import sys
import json
import pprint
import fnmatch

token = 'abc'


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def get_auth(f):
    """Get authentication token from config file"""
    config = configparser.ConfigParser()
    config.read_file(f)
    ret = config.get('github', 'token', fallback='Auth configuration not usable!')
    return ret #config['github']['token']


def token_auth(req):
    """Helper function for the session"""
    req.headers['Authorization'] = f'token {token}'
    return req


def validate_repo_names(repos):
    """Tell whether repo names are valid"""
    print('Validating repo names:')
    for r in repos:
        s = r.split('/')
        if (s[0] == r):
            print(f'  Not valid: {r}.')
            return r
        if (s[0] == '') or (s[1] == ''):
            print(f'  Not valid: {r}.')
            return r
        if (s[0].find('/') != -1) or (s[1].find('/') != -1):
            print(f'  Not valid: {r}.')
            return r
        print(f'  {r}: OK')
    return True


def create_session(config_auth):
    """Create session using the access token"""
    print('Creating GitHub session.')
    global token
    token = get_auth(config_auth)
    session = requests.Session()
    session.headers = {'User-Agent': 'soucevi1'}
    session.auth = token_auth
    return session


def get_repo_prs(r, state, base, session):
    """
    Get all pull requests of a given repository
        r: string 'author/repo-name'
        state: state of the PR
        base: base branch
        session: open and authenticated session
    """
    print(f'Getting PRs of {r}')
    payload = {'state': state, 'base': base}
    pulls = session.get(f'https://api.github.com/repos/{r}/pulls', params=payload)
    if pulls.status_code != 200:
        return False
    return pulls.json()

def get_pr_files(r, session, pull_num):
    """
    Get json containing all the files that are modified in the current pull request
        r: string 'author/repo-name'
        session: open and authenticated session
        pull_num: number of the pull request
    """
    print(f'Getting file json of {r}: PR {pull_num}')
    pull_files = session.get(f'https://api.github.com/repos/{r}/pulls/{pull_num}/files')
    if pull_files.status_code != 200:
        return False
    return pull_files.json()


def get_pr_filenames(fj):
    """
    Parse filenames from file json
        fj: files json
    """
    print('Parsing filenames from the json file')
    fns = []
    for i in range(len(fj)):
        fns.append(fj[i]['filename'])
        #print(f"  filename: {fj[i]['filename']}")
    return fns


def get_labels_to_add(filenames, pattern_dict):
    """
    Get labels to add to the PR
        filenames: list of fns
        paterns: dict "label:[pattern, p...]"
    """
    ret = []
    for fn in filenames:
        for entry in pattern_dict:
            for i in range(len(pattern_dict[entry])):
                if fnmatch.fnmatch(fn, pattern_dict[entry][i]):
                    ret.append(entry)
    return ret


def get_label_patterns(file):
    """
    Parse fn patterns from config file
    """
    config = configparser.ConfigParser()
    config.read_file(file)
    if config.has_section('labels') == False:
        return {}
    opts = config.options('labels')
    ret = {}
    for o in opts:
        patterns = config.get('labels', o)
        patts = patterns.split('\n')
        if '' in patts:
            patts.remove('')
        ret[o] = patts
    print(ret)
    return ret
    

def get_labels_to_keep(labels_curr, pattern_dict):
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


def add_labels(repo, pull_num, labels, pull_info, session):
    payload = {'labels': labels, 
               'title': pull_info['title'], 
               'body': pull_info['body'],
               'state': pull_info['state'],
               'milestone': pull_info['milestone']
               'assignees': pull_info['assignees']}
    ret = session.put(f'https://api.github.com/repos/{repo}/issues/{pull_num}', 
        params=payload)
    if ret.status_code != 200:
        return False
    return True


def get_added_labels(l_new, l_old):
    ret = []
    for l in l_new:
        if l in l_old:
            continue
        else:
            ret.append(l)
    return ret


def get_removed_labels(l_new, l_old):
    ret = []
    for l in l_old:
        if l in l_new:
            continue
        else:
            ret.append(l)
    return ret


def get_labels_kept(l_new, l_old):
    ret = []
    for l in l_new:
        if l in l_old:
            ret.append(l)
    return ret


@click.command()
@click.argument('REPOSLUGS', nargs=-1)
@click.option('-s','--state', type=click.Choice(['open', 'closed', 'all']),
    help='Filter pulls by state.  [default: open]', default='open')
@click.option('-d/-D','--delete-old/--no-delete-old', 
    help='Delete labels that do not match anymore. [default: True]', default=True)
@click.option('-b', '--base', metavar='BRANCH', 
    help='Filter pulls by base (PR target) branch name.')
@click.option('-a', '--config-auth', metavar='FILENAME', 
    type=click.File('r'), help='File with authorization configuration.')
@click.option('-l', '--config-labels', metavar='FILENAME', 
    type=click.File('r'), help='File with labels configuration.')

def main(config_auth, config_labels, reposlugs, state, delete_old, base):
    """CLI tool for filename-pattern-based labeling of GitHub PRs"""
    colorama.init(autoreset=True)
    # Validate inputs and parameters
    if config_auth == None:
        print('Auth configuration not supplied!')
        sys.exit(1)
    if config_labels == None:
        print('Labels configuration not supplied!')
        sys.exit(1)
    rep = validate_repo_names(reposlugs)
    if rep != True:
        print(f'Reposlug {rep} not valid')
        sys.exit(1)

    fpatterns = get_label_patterns(config_labels)
    if fpatterns == {}:
        print('Labels configuration not usable!')
        sys.exit(1)

    # Open a session
    session = create_session(config_auth)

    # Iterate through all the repositories
    for r in reposlugs:
        # Get all PRs of the current repo
        pulls_json = get_repo_prs(r, state, base, session)
        if pulls_json == False:
            print(color.BOLD + 'REPO' + color.END + r + ' - ' + color.RED + color.BOLD + 'FAIL')
            continue
        print(color.BOLD + 'REPO' + color.END + r + ' - ' + color.GREEN + color.BOLD + 'OK')
        # For each PR find its number, current labels and get info about the files
        for n in range(len(pulls_json)):
            pull_num = pulls_json[n]['number']
            labels_current = pulls_json[n]['labels']
            pull_info = {'milestone': pulls_json[n]['milestone'],
                         'state': pulls_json[n]['state'],
                         'title': pulls_json[n]['title'],
                         'body': pulls_json[n]['body'],
                         'assignees': pulls_json[n]['assignees']}
            pull_files_json = get_pr_files(r, session, pull_num)
            if pull_files_json == False:
                print(color.BOLD + '  PR' + color.END + f'https://github.com/{r}/pull/{pull_num} - ' + color.BOLD + color.RED + 'FAIL')
                continue
            pull_filenames = get_pr_filenames(pull_files_json)   
            labels_new = get_labels_to_add(pull_filenames, fpatterns)              

            labels_to_add = []
            fl = False
            if delete_old == True:
                labels_to_keep = get_labels_to_keep(labels_current)
                labels_to_add.append(labels_to_keep)
                labels_to_add.append(labels_new)
                fl = add_labels(r, pull_num, labels_to_add, pull_info, session)

            else:
                labels_to_add.append(labels_current)
                labels_to_add.append(labels_new)
                labels_new.append(labels_current)
                fl = add_labels(r, pull_num, labels_to_add, pull_info, session)

            if fl == True:
                print(color.BOLD + '  PR' + color.END + f'https://github.com/{r}/pull/{pull_num} - ' + color.BOLD + color.GREEN + 'OK')
                labels_added = get_added_labels(labels_new, labels_current)
                labels_removed = get_removed_labels(labels_new, labels_current)
                labels_kept = get_labels_kept(labels_new, labels_current)
                for l in labels_added:
                    print('    ' + color.GREEN + f'+ {l}' + color.END)
                for l in labels_removed:
                    print('    ' + color.RED + f'+ {l}' + color.END)
                for l in labels_kept:
                    print(f'    + {l}')
            else:
                print(color.BOLD + '  PR' + color.END + f'https://github.com/{r}/pull/{pull_num} - ' + color.BOLD + color.RED + 'FAIL')




            # TODO: nejspis uz jen otestovat + ostranit prebytecne vypisy


    # pro kazdy repozitar:
    #     pouzit GET /repos/:owner/:repo/pulls k vypsani vsech PR daneho repozitare
    #           (GET bere jako parametr state a base)
    #     pro kazdy PR:
    #           podivat se, co se meni
    #           srovnat s konfigurakem, upravit tag (pomoci Issue API)



if __name__ == '__main__':
    main()