"""
request payload processing module
"""

from web_crawler.utils import custom_exceptions as _exceptions


def parse_payload(request):
    """
    parse payload
    """
    try:
        payload = request.json
    except Exception as err:
        raise _exceptions.PayloadParseError(
            'Unable to parse payload. Error {}'.format(err.message))
    return payload


def check_required_keys(payload, required_keys):
    """
    check required keys
    :param payload:
    :param required_keys:
    :return:
    """
    missing_keys = set(required_keys) - set(payload.keys())
    if missing_keys:
        raise _exceptions.MissingKeysError(
            'Missing required keys {}'.format(', '.join(missing_keys))
        )
