import sys
import os

from awacs import AWSObject, AWSHelperFn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


AWSObject.__repr__ = lambda self: str(self.JSONrepr())
AWSHelperFn.__repr__ = lambda self: str(self.to_json())