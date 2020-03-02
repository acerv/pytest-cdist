"""
cdist library.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from cdist.redis import RedisResource


def get_resource(rtype, **kwargs):
    """
    Return a resource according with resource type.

    Args:
        rtype   (str): resource type.
        kwargs (dict): resource object parameters.

    Returns:
        Resource: a resource communication object. None if type is not supported.
    """
    resource = None
    if rtype == "redis":
        resource = RedisResource(**kwargs)

    return resource
