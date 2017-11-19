import awacs.aws

# Monkey Patching equality that's not implemented in the library

def pdeq(self, other):
    if isinstance(other, self.__class__):
        return self.to_json() == other.to_json()
    else:
        return False


def pdne(self, other):
    return not self.__eq__(other)

def awsrepr(self):
    return str(self.properties)

def actionrepr(self):
    return "'"+self.prefix + ':' + self.action+"'"

awacs.aws.PolicyDocument.__eq__ = pdeq
awacs.aws.PolicyDocument.__ne__ = pdne
awacs.AWSObject.__repr__ = awsrepr
awacs.aws.Action.__repr__ = actionrepr