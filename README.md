# TrailScraper

[![PyPi Release](https://img.shields.io/pypi/v/trailscraper.svg)](https://pypi.python.org/pypi/trailscraper)
[![Build Status](https://travis-ci.org/flosell/trailscraper.svg?branch=master)](https://travis-ci.org/flosell/trailscraper)

A command-line tool to get valuable information out of AWS CloudTrail

## Installation

```bash
$ pip install trailscraper
```

## Usage

```bash
# Download some logs
$ trailscraper download --bucket <some-bucket> \
                        --account-id <some account id> \
                        --region <some region to look at> \ 
                        --past-days <number of past days to look at> \
# Generate an IAM Policy  
$ trailscraper generate
{
    "Statement": [
        {
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVolumes",
                "ec2:DescribeVpcs",
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "sts:AssumeRole"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:iam::1111111111:role/someRole"
            ]
        }
    ],
    "Version": "2012-10-17"
} 
```

## Development

```bash
$ ./go setup   # set up venv, dependencies and tools
$ ./go test    # run some tests
$ ./go check   # run some style checks
$ ./go         # let's see what we can do here
```

### Troubleshooting
#### Click thinks you are in an ASCII environment 

`Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment.`

Set these environment variables:
```
LC_ALL=C.UTF-8
LANG=C.UTF-8
```
