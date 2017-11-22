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

setup(
    name='trailscraper',
    version='0.1',
    description='A command-line tool to get valuable information out of AWS CloudTrail',
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
)
