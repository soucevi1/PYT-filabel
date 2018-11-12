import filabel.github
import betamax
import requests
import pytest
import os
import json


label_file = 'tests/fixtures/labels2.cfg'
auth_file = 'tests/fixtures/credentials.cfg'
empty_file = 'tests/fixtures/empty.cfg'
response_file = 'tests/fixtures/resp_json.json'
label_json = 'tests/fixtures/labels.json'
TOKEN = ''
TEST_REPO = ''
labels = {"frontend": ["*/templates/*", "static/*"], 
          "backend": ["logic/*"],
          "docs": ["*.md", "*.rst", "*.adoc", "LICENSE", "docs/*"], 
          "file1": ["file1111111*"], 
          "file10": ["file10*"], "file9": ["file9*"]}



with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    if 'AUTH_FILE' in os.environ:
        with open(os.environ['AUTH_FILE']) as af:
            TOKEN = filabel.github.get_auth(af)
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
	

def test_get_auth():
	with open(auth_file) as f:
		t = filabel.github.get_auth(f)
	assert t is not False

	with open(empty_file) as f:
		t = filabel.github.get_auth(f)
	assert t is False


def test_get_labels():
    global labels
    with open(label_file) as f:
       l = filabel.github.get_label_patterns(f)
    assert l is not False
    assert l == labels
    with open(empty_file) as f:
        t = filabel.github.get_label_patterns(f)
    assert t is False


def test_create_session(betamax_session):
	with open(auth_file) as f:
		s = filabel.github.create_session(f, betamax_session)
	assert 'User-Agent' in s.headers


def test_get_filenames_from_json():
    with open(response_file) as f:
        jdata = json.load(f)
        fns = filabel.github.get_pr_filenames(jdata)
        assert 'aaaa' in fns
        assert 'bbbb' in fns
        assert 'cccc' in fns
        assert 'dddd' in fns


def test_get_pr_files(testing_session):
    pf = filabel.github.get_pr_files(TEST_REPO, testing_session, 1)
    assert pf is not False
    res = ['aaaa', 'bbbb', 'cccc', 'dddd']
    assert set(res) == set(pf)
    pf = filabel.github.get_pr_files(TEST_REPO, testing_session, 2)
    assert pf is not False
    assert len(pf) == 222
    for i in range(1,223):
        assert f'file{i}' in pf


def test_all_labels():
    global labels
    files = ['aaaa', "ahoj.md", "static/xyz", "file100", "file999"]
    l = filabel.github.get_all_labels(files, labels)
    res = ["frontend", "docs", "file10", "file9"]
    assert len(l) == 4
    assert set(res) == set(l)


def test_keeping_unknown_labels():
    global labels
    current_labels = ['abcd', 'docs', 'backend', 'pivo']
    l = filabel.github.get_unknown_labels_to_keep(current_labels, labels)
    assert set(l) == set(['abcd', 'pivo']) 


def test_get_label_names_from_json():
    with open(label_json) as f:
        l = filabel.github.get_label_names(json.load(f))
        assert set(l) == set(['bug', 'enhancement'])


def test_test_labels_added(testing_session):
    l = ['bug']
    r = filabel.github.test_labels_added(TEST_REPO, 1, l, testing_session)
    assert r == True


def test_add_labels(testing_session):
    l = ['abc']
    r = filabel.github.add_labels(TEST_REPO, 1, l, testing_session)
    assert r == True