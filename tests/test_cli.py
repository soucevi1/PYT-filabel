import click
from click.testing import CliRunner
import filabel.cli
import pytest
import betamax
import os
import configparser


valid_repo_lists = (['ahoj/ahoj', 'asd4/avr5w'], 
					['ahoj/ahoj', 'a/a'],
					['aa/vvk'])
invalid_repo_lists = (['aaa', '/abcd', '/', 'vwvws/'], 
					  ['aaa/aaa', 'aaa', 'aa/bb'], 
					  ['/abdc', 'cdf/egf'],
					  [''])
TOKEN = ''
TEST_REPO = ''
label_file = 'tests/fixtures/labels2.cfg'
auth_file = 'tests/fixtures/credentials.cfg'
empty_file = 'tests/fixtures/empty.cfg'
labels = {"frontend": ["*/templates/*", "static/*"], 
          "backend": ["logic/*"],
          "docs": ["*.md", "*.rst", "*.adoc", "LICENSE", "docs/*"], 
          "file1": ["file1111111*"], 
          "file10": ["file10*"], "file9": ["file9*"]}


def get_token(f):
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


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    if 'AUTH_FILE' in os.environ:
        with open(os.environ['AUTH_FILE']) as af:
            TOKEN = get_token(af)
        config.default_cassette_options['record_mode'] = 'all'
    else:
        TOKEN = 'false_token'
        config.default_cassette_options['record_mode'] = 'none'
    if 'TEST_REPO' in os.environ:
        TEST_REPO = os.environ['TEST_REPO']
    else:
        TEST_REPO = 'soucevi1/filabel-testrepo1'
    config.define_cassette_placeholder('<TOKEN>', TOKEN)


@pytest.fixture
def testing_session(betamax_session):
	with open(auth_file) as f:
		s = filabel.github.create_session(f, betamax_session)
	return s


@pytest.mark.parametrize('rname', valid_repo_lists)
def test_valid_repos(rname):
	v = filabel.cli.validate_repo_names(rname)
	assert v == True

@pytest.mark.parametrize('rname', invalid_repo_lists)
def test_invalid_repo_names(rname):
	v = filabel.cli.validate_repo_names(rname)
	assert v != True	


def test_get_repo_prs(testing_session):
	p = filabel.cli.get_repo_prs(TEST_REPO, 'open', 'master', testing_session)
	assert len(p) == 2


def test_get_added_labels():
	old_labels = ['ahoj', 'pivo', 'rum']
	new_labels = ['pangalaktickymagecloumak', 'voda', 'pivo', 'rum']
	r = filabel.cli.get_added_labels(new_labels, old_labels)
	assert set(r) == set(['pangalaktickymagecloumak', 'voda'])


def test_get_new_in_current():
	old_labels = ['frontend', 'docs', 'rum']
	new_labels = ['frontend', 'backend', 'pivo', 'rum']
	r = filabel.cli.get_new_in_current(new_labels, old_labels, labels)
	assert set(r) == set(['frontend'])


def test_get_removed():
	old_labels = ['frontend', 'docs', 'rum']
	new_labels = ['frontend', 'backend', 'pivo', 'rum']
	r = filabel.cli.get_removed(new_labels, old_labels, labels)
	assert set(r) == set(['docs'])


def test_no_labels():
	runner = CliRunner()
	result = runner.invoke(filabel.cli.main, ['-a', auth_file, 
		 '-s', 'open', '--delete-old', '-b', 'master', TEST_REPO])
	assert 'Labels configuration not supplied!\n' == result.output 


def test_empty_labels():
	runner = CliRunner()
	result = runner.invoke(filabel.cli.main, ['-a', auth_file, '-l', empty_file, 
		 '-s', 'open', '--delete-old', '-b', 'master', TEST_REPO])
	assert 'Labels configuration not usable!\n' == result.output 


def test_no_auth():
	runner = CliRunner()
	result = runner.invoke(filabel.cli.main, ['-l', empty_file, 
		 '-s', 'open', '--delete-old', '-b', 'master', TEST_REPO])
	assert 'Auth configuration not supplied!\n' == result.output 


def test_empty_auth():
	runner = CliRunner()
	result = runner.invoke(filabel.cli.main, ['-a', empty_file, '-l', label_file, 
		 '-s', 'open', '--delete-old', '-b', 'master', TEST_REPO])
	assert 'Auth configuration not usable!\n' == result.output


def test_invalid_repo():
	runner = CliRunner()
	result = runner.invoke(filabel.cli.main, ['-a', empty_file, '-l', label_file, 
		 '-s', 'open', '--delete-old', '-b', 'master', 'aaa'])
	assert 'Reposlug aaa not valid!\n' == result.output	