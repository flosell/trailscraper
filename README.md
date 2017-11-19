# TrailScraper

A command-line tool to get valuable information out of AWS CloudTrail

## Usage
none yet...

## Development

```bash
$ ./go setup   # set up venv and dependencies
$ source ./go enable  # enable venv
$ ./go         # let's see what we can do here
```

### Troubleshooting
#### `Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment.`

Set these environment variables:
```
LC_ALL=C.UTF-8
LANG=C.UTF-8
```
