import filabel.cli
import pytest


valid_repo_lists = (['ahoj/ahoj', 'asd4/avr5w'], 
					['ahoj/ahoj', 'a/a'],
					['aa/vvk'])
invalid_repo_lists = (['aaa', '/abcd', '/', 'vwvws/'], 
					  ['aaa/aaa', 'aaa', 'aa/bb'], 
					  ['/abdc', 'cdf/egf'],
					  [''])


@pytest.mark.parametrize('rname', valid_repo_lists)
def test_valid_repos(rname):
	v = filabel.cli.validate_repo_names(rname)
	assert v == True

@pytest.mark.parametrize('rname', invalid_repo_lists)
def test_invalid_repo_names(rname):
	v = filabel.cli.validate_repo_names(rname)
	assert v != True	

