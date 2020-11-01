# Changelog

This changelog contains a loose collection of changes in every release including breaking changes to the API.

The format is based on [Keep a Changelog](http://keepachangelog.com/)

## 0.7.0

### Added 

* Support for Python 3.9

### Removed

* **Removed official support for Python 3.5**. TrailScraper might still run but we no longer actively test for it

## 0.6.4

### Fixed

* Fixed Docker images that threw a `ModuleNotFoundError`

### Changed

* Performance tweaks
  * `trailscraper download` uses smarter directory listing to improve performance with large date ranges and little new data
  * `trailscraper download` now downloads files in parallel
  * Minor performance improvements in `trailscraper select`

## 0.6.2 and 0.6.3

(skipeed because of continuing release-script issues)

## 0.6.1

(same as 0.6.1, just fixing inconsistent release)

## 0.6.0

### Added

* Support for Python 3.7 and 3.8
* Support for org-level trails (#101)

### Fixed

* `trailscraper guess` was not working when installed through homebrew or pip (#110)

### Removed

* **Removed official support for Python 2.7 and 3.4**. TrailScraper might still run but we no longer actively test for it

## 0.5.1

### Added

* New command `guess` to extend existing policy by guessing matching actions #22

### Fixed

* Fixed parsing events that contain resources without an ARN (e.g. `s3:ListObjects`) #51

## 0.5.0

**Breaking CLI changes**: split up `generate-policy` into `select` and `generate` (#38)

### Added

* New command `select` to print all CloudTrail records matching a filter to stdout
* New command `generate` to take CloudTrail records from stdin and generate a policy for it

### Changed

* New command `select` defaults to not filtering at all whereas `generate-policy` filtered for recent events by default.
  Changed to make filtering more explicit and predictable instead of surprising users who wonder why their events don't show up

### Removed

* Removed command `generate-policy`, replaced with `select` and `generate`. Use pipes to produce the same behavior: 
  ```bash
  $ trailscraper select | trailscraper generate
  ```

## 0.4.4

### Fixed

* Made trailscraper timezone-aware. Until now, trailscraper implicitly treated everything as UTC, meaning relative timestamps (e.g. `now`, `two hours ago`) didn't work properly when filtering logfiles to download or records to generate from. (#39) 

### Added

* New command `trailscraper last-event-timestamp` to get the last known event timestamp.
* New flag `trailscraper download --wait` to wait until events for the specified timeframe are found.
  Useful if you are waiting for CloudTrail to ship logs for a recent operation.


## 0.4.3

_skipped because of release-problems_

## 0.4.2

### Fixed

* Fixed various special cases in mapping CloudTrail to IAM Actions:
  * API Gateway
  * App Stream 2
  * DynamoDB Streams
  * Lex
  * Mechanical Turk
  * S3
  * STS
  * Tagging

## 0.4.1

### Fixed

* Ignore record files that can't be read (e.g. not valid GZIP) in Python 2.7 (was only working in Python 3.* before)
* Fixed permissions generated for services that include the API version date (e.g. Lambda, CloudFront) (#20)

## 0.4.0

### Added

* Support for CloudTrail `lookup_events` API that allows users to generate a policy without downloading logs from an S3 bucket.
  Note that this API only returns _["create, modify, and delete API calls"](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events-supported-services.html)_
* `trailscraper download` now supports `--from` and `--to` flags to specify the timeframe that should be downloaded. Accepts precise (e.g. "2017-10-12") and relative (e.g. "-2days") arguments.
* `trailscraper generate-policy` now supports `--from` and `--to` to filter events to consider for the generated policy. Accepts precise (e.g. "2017-10-12") and relative (e.g. "-2days") arguments.

* Performance optimizations: `generate-policy` only reads logfiles for the timeframe requested

* Added `--version` command line argument

### Changed

* Set more flexible dependencies

### Removed

* Removed `--past-days` parameter in `trailscraper download`. Was replaced by `--from` and `--to` (see above)

### Fixed

* Ignore record files that can't be read (e.g. not valid GZIP)

## 0.3.0

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
