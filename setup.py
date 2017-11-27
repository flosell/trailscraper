from setuptools import setup, find_packages

requirements = [
    'boto3==1.4.7',
    'click==6.7',
    'awacs==0.7.2'
]

setup_requirements = [
    'pytest-runner==3.0',
]

test_requirements = [
    'pytest==3.2.5',
    'pytest-catchlog==1.2.2',
    'freezegun==0.3.9',
    'moto==1.1.24',
]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()


setup(
    name='trailscraper',
    version='0.2',
    description='A command-line tool to get valuable information out of AWS CloudTrail',
    long_description=readme + '\n\n' + changelog,
    url='http://github.com/flosell/trailscraper',
    author='Florian Sellmayr',
    author_email='florian.sellmayr@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(include=['trailscraper']),
    zip_safe=False,
    entry_points={
        'console_scripts': ['trailscraper=trailscraper.cli:root_group'],
    },
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    keywords=["aws","cloud","iam","cloudtrail","trailscraper"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities',
        'Topic :: System :: Systems Administration',
        'Topic :: Security',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
    # workaround until cloudtools/awacs#87 is merged
    dependency_links=['http://github.com/flosell/awacs/tarball/add_equality_and_hashes#egg=awacs-0.7.2']
)
