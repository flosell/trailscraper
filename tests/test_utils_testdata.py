import os


def cloudtrail_data(filename):
    return os.path.join(cloudtrail_data_dir(), filename)


def cloudtrail_data_dir():
    return os.path.join(os.path.dirname(__file__), 'cloudtrail', 'data')