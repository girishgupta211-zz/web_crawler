"""
Response module
"""


def response(data=None, meta_data=None, error_dict=None):
    """
    Prepare response
    """
    if not data:
        data = {}
    if not meta_data:
        meta_data = {}
    if not error_dict:
        error_dict = {}

    template = {
        'meta_data': meta_data,
        'error': {
            'err_msg': None,
            'err_code': None,
            'err_str': None
        },
        'results': data
    }
    status_code = error_dict.pop('http_status_code', 200)
    template['error'].update(**error_dict)
    return template, status_code
