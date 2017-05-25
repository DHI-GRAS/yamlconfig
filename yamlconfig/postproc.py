

class RequiredKeysError(Exception):
    pass


def check_required_keys(configdict, required_keys=None):
    if required_keys is None:
        return
    if not set(configdict).issuperset(set(required_keys)):
        raise RequiredKeysError('Config keys set does not include required: {}'.format(required_keys))
