"""
CLI module of filabels program. Used to manually run the program and label the desired pull requests.
"""

import click
import colorama
import json
import sys
import pprint
import os
from filabel.github import *


"""
Helper class used to write the output
"""
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


def validate_repo_names(repos):
    """
    Checks whether repository name is '{username}/{repo}'
        :param repos: list of repository names
        :type repos: list
        :returns: True if all are OK, repo name of the one that is not
        :rtype: bool, string
    """
    for r in repos:
        s = r.split('/')
        if (s[0] == r):
            return r
        if (s[0] == '') or (s[1] == ''):
            return r
        if (s[0].find('/') != -1) or (s[1].find('/') != -1):
            return r
    return True



def get_repo_prs(r, state, base, session):
    """
    Get all pull requests of a given repository
        :param r: repository name 'author/repo-name'
        :param state: state of the PR
        :param base: base branch
        :param session: open and authenticated session
        :type r: string
        :type state: string
        :type base: string
        :type session: requests.Session()
        :returns: list of JSON of the pull requests, False if something goes wrong
        :rtype: list, bool
    """
    payload = {'state': state, 'base': base}
    pulls = session.get(f'https://api.github.com/repos/{r}/pulls', params=payload)
    if pulls.status_code != 200:
        return False

    pjlist = pulls.json()
    if 'Link' in pulls.headers:
        while True:
            links = requests.utils.parse_header_links(pulls.headers['Link'])
            n_flag = False
            for l in links:
                if l['rel'] == 'next':
                    pulls = session.get(l['url'])
                    if pulls.status_code != 200:
                        return False
                    n_flag = True
                    break            
            if n_flag == False:
                break 
            pjlist += pulls.json()
    return pjlist


def get_added_labels(l_new, l_old):
    """
    Get labels that are new to this PR
        :param l_new: new labels to be added
        :param l_old: labels that were already in the PR
        :type l_new: list
        :type l_old: list
        :returns: list of labels that were added
        :rtype: list
    """
    ret = []
    for l in l_new:
        if l in l_old:
            continue
        else:
            ret.append(l)
    return ret


def get_new_in_current(l_new, l_old, pattern_dict):
    """
    Get those labels, that are supposed to be added but were already there and known
        :param l_new: new labels
        :param l_old: old labels
        :param pattern_dict: directory of patterns that are used to match the filenames
        :type l_new: list
        :type l_old: list
        :type pttern_dict: dictionary
        :returns: list of knwon labels to be added, that were already in the pull request
        :rtype: list
    """
    ret = []
    ret2 = []
    for l in l_new:
        if l in l_old:
            ret.append(l)
    for l in ret:
        if l in pattern_dict:
            ret2.append(l)
    return ret2


def get_current_in_all(l_to_add, l_old, pattern_dict):
    """
    Get those labels that were already there and known
        :param l_to_add: new labels
        :param l_old: old labels
        :type l_to_add: list
        :type l_old: list
        :param pattern_dict: directory of patterns that are used to match the filenames
        :type pattern_dict: dictionary
        :returns: list of the known assigned labels
        :rtype: list
    """
    ret = []
    ret2 = []
    for l in l_to_add:
        if l in l_old:
            ret.append(l)
    for l in ret:
        if l in pattern_dict:
            ret2.append(l)
    return ret2




def get_removed(l_new, l_old, fpatterns):
    """
    Get those labels that are supposed to be removed
        :param l_new:  new labels
        :param l_old: old labels
        :param pattern_dict: directory of patterns that are used to match the filenames
        :type l_new: list
        :type l_old: list
        :type pattern_dict: ditionary
        :returns: list of removed labels
        :rtype: list
    """
    ret = []
    ret2 = []
    for l in l_old:
        if l in fpatterns:
            ret.append(l)
    for l in ret:
        if l not in l_new:
            ret2.append(l)
    return ret2


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
    """
    Main function of the CLI module. For every reposlug it finds all its PRs and sets its labels.
        :param config_auth: name of the configuration file with credentials
        :param config_labels: name of the configuration file with label rules
        :param reposlugs: list of repo names ('owner/reponame')
        :param state: state of the pull requests to be labeled (open, closed, all)
        :param delete_old: flag indicating that old unused labels should be deleted from the PR
        :param base: base branch
        :type config_auth: string
        :type config_labels: string
        :type reposlugs: list of strings
        :type state: string
        :type delete_old: bool
        :type base: string
    """
    colorama.init(autoreset=True)
    # Validate inputs and parameters
    if config_auth == None:
        print('Auth configuration not supplied!', file=sys.stderr)
        sys.exit(1)
    if config_labels == None:
        print('Labels configuration not supplied!', file=sys.stderr)
        sys.exit(1)
    rep = validate_repo_names(reposlugs)
    if rep != True:
        print(f'Reposlug {rep} not valid!', file=sys.stderr)
        sys.exit(1)

    fpatterns = get_label_patterns(config_labels)
    if fpatterns == False:
        print('Labels configuration not usable!', file=sys.stderr)
        sys.exit(1)

    # Open a session
    session = create_session(config_auth)
    if session == False:
        print('Auth configuration not usable!', file=sys.stderr)
        sys.exit(1)        

    # Iterate through all the repositories
    for r in reposlugs:
        # Get all PRs of the current repo
        pulls_json = get_repo_prs(r, state, base, session)
        if pulls_json == False:
            print(color.BOLD + 'REPO ' + color.END + r + ' - ' + color.RED + color.BOLD + 'FAIL')
            continue
        print(color.BOLD + 'REPO ' + color.END + r + ' - ' + color.GREEN + color.BOLD + 'OK')
        # For each PR find its number, current labels and get info about the files
        for n in range(len(pulls_json)):
            pull_num = pulls_json[n]['number']
            labels_current = get_current_labels(pulls_json[n]['labels'])
            pull_files_json_list = get_pr_files(r, session, pull_num)
            if pull_files_json_list == False:
                print(color.BOLD + '  PR ' + color.END + f'https://github.com/{r}/pull/{pull_num} - ' + color.BOLD + color.RED + 'FAIL')
                continue
            pull_filenames = pull_files_json_list#get_pr_filenames(pull_files_json_list)   
            labels_new = get_all_labels(pull_filenames, fpatterns)              

            labels_to_add = []
            labels_plus = []
            labels_minus = []
            labels_eq = []
            fl = False
            if delete_old == True:
                # Delete old
                u_labels_to_keep = get_unknown_labels_to_keep(labels_current, fpatterns)
                labels_to_add = labels_new#labels_to_keep + labels_new
                labels_to_add += u_labels_to_keep
                labels_to_add = list(set(labels_to_add))
                fl = add_labels(r, pull_num, labels_to_add, session)
                labels_plus = get_added_labels(labels_new, labels_current)
                labels_eq = get_new_in_current(labels_new, labels_current, fpatterns)
                labels_minus = get_removed(labels_new, labels_current, fpatterns)                

            else:
                # No delete old
                labels_to_add = labels_new + labels_current
                labels_to_add = list(set(labels_to_add))
                fl = add_labels(r, pull_num, labels_to_add, session)
                labels_plus = get_added_labels(labels_new, labels_current)
                labels_eq = get_current_in_all(labels_new, labels_current, fpatterns)

            if fl == True:
                labels_to_print = []
                for x in labels_plus:
                    labels_to_print.append(('+', x))
                for x in labels_minus:
                    labels_to_print.append(('-', x))
                for x in labels_eq:
                    labels_to_print.append(('=', x))
                labels_to_print.sort(key=lambda tup: tup[1])
                print(color.BOLD + '  PR ' + color.END + f'https://github.com/{r}/pull/{pull_num} - ' + color.BOLD + color.GREEN + 'OK')
                for l in labels_to_print:
                    if l[0] == '+':
                        print('    ' + color.GREEN + f'+ {l[1]}' + color.END)
                    elif l[0] == '-':
                        print('    ' + color.RED + f'- {l[1]}' + color.END)
                    elif l[0] == '=':
                        print(f'    = {l[1]}')
            else:
                print(color.BOLD + '  PR ' + color.END + f'https://github.com/{r}/pull/{pull_num} - ' + color.BOLD + color.RED + 'FAIL')
