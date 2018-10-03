import click
import configparser
import requests
import sys
import json
import pprint

token = 'abc'

def get_auth(f):
    """Get authentication token from config file"""
    config = configparser.ConfigParser()
    config.read_file(f)
    return config['github']['token']

def token_auth(req):
    """Helper function for the session"""
    req.headers['Authorization'] = f'token {token}'
    return req

def validate_repo_names(repos):
    """Tell whether repo names are valid"""
    for r in repos:
        s = r.split('/')
        if (s[0] == r):
            return r
        if (s[0] == '') or (s[1] == ''):
            return r
        if (s[0].find('/') != -1) or (s[1].find('/') != -1):
            return r 
    return True

def create_session(config_auth):
    """Create session using the access token"""
    global token
    token = get_auth(config_auth)
    session = requests.Session()
    session.headers = {'User-Agent':'soucevi1'}
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
    payload = {'state':state, 'base':base}
    pulls = session.get(f'https://api.github.com/repos/{r}/pulls', params=payload)
    return pulls.json()

def get_pr_files(r, session, pull_num):
    """
    Get json containing all the files that are modified in the current pull request
        r: string 'author/repo-name'
        session: open and authenticated session
        pull_num: number of the pull request
    """
    pull_files = session.get(f'https://api.github.com/repos/{r}/pulls/{pull_num}/files')
    return pull_files.json()

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

    # Open a session
    session = create_session(config_auth)

    # Iterate through all the repositories
    for r in reposlugs:
        # Get all PRs of the current repo
        pulls_json = get_repo_prs(r, state, base, session)
        # For each PR find its number and get info about the files
        for n in range(len(pulls_json)):
            pull_num = pulls_json[n]['number']
            pull_files_json = get_pr_files(r, session, pull_num)
            pprint.pprint(pull_files_json)
        

            # TODO: z file jsonu dostat nazvy souboru


    # pro kazdy repozitar:
    #     pouzit GET /repos/:owner/:repo/pulls k vypsani vsech PR daneho repozitare
    #           (GET bere jako parametr state a base)
    #     pro kazdy PR:
    #           podivat se, co se meni
    #           srovnat s konfigurakem, upravit tag (pomoci Issue API)



if __name__ == '__main__':
    main()