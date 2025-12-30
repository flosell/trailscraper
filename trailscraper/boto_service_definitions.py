"""Helper Methods to get service definition information out of the boto library"""
import gzip
import json
from importlib.resources import files

import botocore.data


def boto_services():
    return [entry.name for entry in files(botocore.data).iterdir() if entry.is_dir()]

def boto_service_definition(servicename):
    servicepath = files(botocore.data).joinpath(servicename)
    all_versions = [entry.name for entry in servicepath.iterdir()]
    all_versions.sort()
    most_recent_version = all_versions[-1]
    b = servicepath.joinpath(most_recent_version).joinpath('service-2.json.gz').read_bytes()
    decompressed = gzip.decompress(b)
    service_definition = json.loads(decompressed)
    return service_definition


def boto_operation_definition(servicename, operationname):
    service_definition = boto_service_definition(servicename)
    return service_definition['operations'][operationname]
