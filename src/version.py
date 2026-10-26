"""Single source of truth for displayed release and downloaded file names."""
APP_VERSION = 'V7.7.6'
FILE_VERSION = APP_VERSION.replace('.', '_')

def download_name(kind, extension):
    if kind not in ('Investigation','Report','Evidence') or extension not in ('md','json'):
        raise ValueError('Unsupported download kind or extension')
    return f'Healthcare_Intelligence_{kind}_{FILE_VERSION}.{extension}'
