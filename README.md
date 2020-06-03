# TrailScraper

[![PyPi Release](https://img.shields.io/pypi/v/trailscraper.svg)](https://pypi.python.org/pypi/trailscraper)
[![Docker Hub Build Status](https://img.shields.io/docker/build/flosell/trailscraper.svg)](https://hub.docker.com/r/flosell/trailscraper/)
[![Build Status](https://travis-ci.org/flosell/trailscraper.svg?branch=master)](https://travis-ci.org/flosell/trailscraper)

A command-line tool to get valuable information out of AWS CloudTrail and a general purpose toolbox for working with IAM policies

## Installation

### OSX

```bash
$ brew install trailscraper
```

### Installation using pip

Requirements:

* Python >= 3.5
* pip

```bash
$ pip install trailscraper
```

### Run directly using docker

```bash
$ docker run --rm --env-file <(env | grep AWS_) -v $HOME/.aws:/root/.aws flosell/trailscraper:latest
```

## Usage

* [Get CloudTrail events matching a filter from CloudTrail API](#get-cloudtrail-events-matching-a-filter-from-cloudtrail-api)
* [Download some logs](#download-some-logs)
* [Download some logs in organisational trails](#download-some-logs-in-organisational-trails)
* [Find CloudTrail events matching a filter in downloaded logs](#find-cloudtrail-events-matching-a-filter-in-downloaded-logs)
* [Generate Policy from some CloudTrail records](#generate-policy-from-some-cloudtrail-records)
* [Extend existing policy by guessing matching actions](#extend-existing-policy-by-guessing-matching-actions)
* [Find CloudTrail events and generate an IAM Policy](#find-cloudtrail-events-and-generate-an-iam-policy)

### Get CloudTrail events matching a filter from CloudTrail API 

```
$ trailscraper select --use-cloudtrail-api \ 
                      --filter-assumed-role-arn some-arn \ 
                      --from 'one hour ago' \ 
                      --to 'now'
{
  "Records": [
    {
      "eventTime": "2017-12-11T15:01:51Z",
      "eventSource": "autoscaling.amazonaws.com",
      "eventName": "DescribeLaunchConfigurations",
...
```

### Download some logs

```
$ trailscraper download --bucket some-bucket \
                        --account-id some-account-id \
                        --region some-other-region \ 
                        --region us-east-1 \
                        --from 'two days ago' \
                        --to 'now' \
```
_Note: Include us-east-1 to download logs for global services. See [below](#why-is-trailscraper-missing-some-events) for details_

### Download some logs in organisational trails

```
$ trailscraper download --bucket some-bucket \
                        --account-id some-account-id \
                        --region us-east-1 \
                        --org-id o-someorgid \
                        --from 'two days ago' \
                        --to 'now'
```

### Find CloudTrail events matching a filter in downloaded logs

```
$ trailscraper select --filter-assumed-role-arn some-arn \ 
                      --from 'one hour ago' \ 
                      --to 'now'
{
  "Records": [
    {
      "eventTime": "2017-12-11T15:01:51Z",
      "eventSource": "autoscaling.amazonaws.com",
      "eventName": "DescribeLaunchConfigurations",
...
```

### Generate Policy from some CloudTrail records

```
$ gzcat some-records.json.gz | trailscraper generate
{
    "Statement": [
        {
            "Action": [
                "ec2:DescribeInstances"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ],
    "Version": "2012-10-17"
} 
```

### Extend existing policy by guessing matching actions

CloudTrail logs might not always contain all relevant actions. 
For example, your logs might only contain the `Create` actions after a terraform run when you really want the delete and
update permissions as well. TrailScraper can try to guess additional statements that might be relevant:  

```
$ cat minimal-policy.json | trailscraper guess
{
    "Statement": [
        {
            "Action": [
                "s3:PutObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "s3:DeleteObject",
                "s3:GetObject",
                "s3:ListObjects"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ],
    "Version": "2012-10-17"
}
$ cat minimal-policy.json | ./go trailscraper guess --only Get
{
    "Statement": [
        {
            "Action": [
                "s3:PutObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ],
    "Version": "2012-10-17"
}
```

### Find CloudTrail events and generate an IAM Policy
```
$ trailscraper select | trailscraper generate
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

## FAQ

### How can I generate policies in CloudFormation YAML instead of JSON? 

TrailScraper doesn't provide this. But you can use [cfn-flip](https://github.com/awslabs/aws-cfn-template-flip) to do it:

```
$ trailscraper select | trailscraper generate | cfn-flip
Statement:
  - Action:
      - ec2:DescribeInstances
    Effect: Allow
    Resource:
      - '*'
```

### How can I generate policies in Terraform HCL instead of JSON? 

TrailScraper doesn't provide this. But you can use [iam-policy-json-to-terraform](https://github.com/flosell/iam-policy-json-to-terraform) to do it:

```
$ trailscraper select | trailscraper generate | iam-policy-json-to-terraform
data "aws_iam_policy_document" "policy" {
  statement {
    sid       = ""
    effect    = "Allow"
    resources = ["*"]

    actions = [
      "ec2:DescribeInstances",
    ]
  }
}
```

### Why is TrailScraper missing some events?

* Make sure you have logs for the `us-east-1` region. Some global AWS services (e.g. Route53, IAM, STS, CloudFront) use this region. For details, check the [CloudTrail Documentation](http://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html#cloudtrail-concepts-global-service-events)

### Why are some TrailScraper-generated actions not real IAM actions?

This is totally possible. Unfortunately, there is no good, machine-readable documentation on how CloudTrail events
map to IAM actions so TrailScraper is using heuristics to figure out the right actions. These heuristics likely don't
cover all special cases of the AWS world.

This is where you come in: If you find a special case that's not covered by TrailScraper, 
please [open a new issue](https://github.com/flosell/trailscraper/issues/new) or, even better, submit a pull request.

For more details, check out the [contribution guide](./CONTRIBUTING.md) 

### Why does click think I am in an ASCII environment? 

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

## Development

```bash
$ ./go setup   # set up venv, dependencies and tools
$ ./go test    # run some tests
$ ./go check   # run some style checks
$ ./go         # let's see what we can do here
```
