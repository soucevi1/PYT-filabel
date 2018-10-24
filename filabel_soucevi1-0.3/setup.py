from setuptools import setup, find_packages


with open('README') as f:
    long_description = ''.join(f.readlines())

#print(find_packages())

setup(
    name='filabel_soucevi1',
    version='0.3',
    description='Automatic labels for GitHub pull requests',
    long_description=long_description,
    author='Vít Souček',
    author_email='soucevi1@fit.cvut.cz',
    license='Public Domain',
    url='https://github.com/soucevi1/PYT-01',
    packages=find_packages(),
    package_data={'filabel': ['templates/*.html']},
    entry_points={
    	'console_scripts': [
    		'filabel = filabel.cli:main',
    	]

    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Flask'
        ],
    zip_safe=False,
    install_requires=[ 'wheel', 'Flask', 'click', 'colorama', 'requests'],

)