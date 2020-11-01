from setuptools import setup, find_packages


def read_file(filename):
    try:
        with open(filename) as readme_file:
            return readme_file.read()
    except:
        return ''

requirements = read_file('requirements.txt')

readme = read_file('README.rst')
changelog = read_file('CHANGELOG.rst')

setup(
    name='trailscraper',
    version='0.6.5',
    description='A command-line tool to get valuable information out of AWS CloudTrail',
    long_description=readme + '\n\n' + changelog,
    url='http://github.com/flosell/trailscraper',
    author='Florian Sellmayr',
    author_email='florian.sellmayr@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(include=['trailscraper','trailscraper.*']),
    package_data={
        "": ["known-iam-actions.txt"],
    },
    zip_safe=False,
    entry_points={
        'console_scripts': ['trailscraper=trailscraper.cli:root_group'],
    },
    install_requires=requirements,
    test_suite='tests',
    keywords="aws cloud iam cloudtrail trailscraper",
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
)
