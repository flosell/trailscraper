# Changelog

This changelog contains a loose collection of changes in every release including breaking changes to the API.

The format is based on [Keep a Changelog](http://keepachangelog.com/)

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
