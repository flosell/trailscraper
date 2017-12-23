# Changelog

This changelog contains a loose collection of changes in every release including breaking changes to the API.

The format is based on [Keep a Changelog](http://keepachangelog.com/)

## 0.3.2

### Added

* Support for CloudTrail `lookup_events` API that allows users to generate a policy without downloading logs from an S3 bucket.
  Note that this API only returns _["create, modify, and delete API calls"](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events-supported-services.html)_

### Changed

* `trailscraper download` now supports `--from` and `--to` flags to specify the timeframe that should be downloaded. Accepts precise (e.g. "2017-10-12") and relative (e.g. "-2days") arguments.
* `trailscraper generate-policy` now supports `--from` and `--to` to filter events to consider for the generated policy. Accepts precise (e.g. "2017-10-12") and relative (e.g. "-2days") arguments.

* Performance optimizations: `generate-policy` only reads logfiles for the timeframe requested

### Fixed

* Ignore record files that can't be read (e.g. not valid GZIP)

## 0.3.1

### Added

* Added `--version` command line argument

### Changed

* Set more flexible dependencies

## 0.3.0

### Changed

### Added

* Support for Python >= 2.7

### Changed

* Do not download CloudTrail Logs from S3 if they already exist in the target folder (#9)
* Removed dependency on fork of the awacs-library to simplify installation and development 

### Fixed

* Bug that led to policy-statements with the same set of actions not being combined properly in some cases (#7) 

## 0.2.0

### Added

* Basic filtering for role-arns when generating policy (#3)

## 0.1.0

_Initial Release_

### Added

* Basic feature to download CloudTrail Logs from S3 for certain accounts and timeframe
* Basic feature to generate IAM Policies from a set of downloaded CloudTrail logs
