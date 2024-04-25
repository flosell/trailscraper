"""Helper Methods to get service definition information out of the boto library"""

import fnmatch
import gzip
import json
from importlib import resources
from pathlib import Path


def boto_service_definition_files():
    """Return paths to all service definition files from botocore"""

    botocore_data_dir = resources.files("botocore") / "data"
    stack = [botocore_data_dir]
    files = []
    while stack:
        for item in stack.pop().iterdir():
            if item.is_dir():
                stack.append(item)
            elif fnmatch.fnmatch(item.name, "service-*.json.gz"):
                files.append(str(item))
    return files


def service_definition_file(servicename):
    """Returns the path to the most recent service definition file for a service"""

    service_definitions_for_service = fnmatch.filter(boto_service_definition_files(),
                                                     "**/" + servicename + "/*/service-*.json.gz")

    service_definitions_for_service.sort()

    return service_definitions_for_service[-1]


def operation_definition(servicename, operationname):
    """Returns the operation definition for a specific service and operation"""
    botocore = resources.files("botocore")
    file = service_definition_file(servicename)
    res = botocore / str(Path(file).relative_to(str(botocore)))
    service_definition = json.loads(gzip.decompress(res.read_bytes()))
    return service_definition["operations"][operationname]
