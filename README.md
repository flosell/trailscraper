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
# Download some logs (including us-east-1 for global aws services)
$ trailscraper download --bucket some-bucket \
                        --account-id some-account-id \
                        --region some-other-region \ 
                        --region us-east-1 \
                        --from 'two days ago' \
                        --to 'now' \
# Generate an IAM Policy  
$ trailscraper generate-policy
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

#### TrailScraper is missing some events

* Make sure you have logs for the `us-east-1` region. Some global AWS services (e.g. Route53, IAM, STS, CloudFront) use this region. For details, check the [CloudTrail Documentation](http://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html#cloudtrail-concepts-global-service-events)

#### TrailScraper generated actions that aren't IAM actions

This is totally possible. Unfortunately, there is no good, machine-readable documentation on how CloudTrail events
map to IAM actions so TrailScraper is using heuristics to figure out the right actions. These heuristics likely don't
cover all special cases of the AWS world.

This is where you come in: If you find a special case that's not covered by TrailScraper, 
please [open a new issue](https://github.com/flosell/trailscraper/issues/new) or, even better, submit a pull request.

For more details, check out the [contribution guide](./CONTRIBUTING.md) 

#### Click thinks you are in an ASCII environment 

`Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment.`

Set environment variables that describe your locale, e.g. :
```
export LC_ALL=de_DE.utf-8
export LANG=de_DE.utf-8
```
or 
```
LC_ALL=C.UTF-8
LANG=C.UTF-8
```
For details, see http://click.pocoo.org/5/python3/#python-3-surrogate-handling

