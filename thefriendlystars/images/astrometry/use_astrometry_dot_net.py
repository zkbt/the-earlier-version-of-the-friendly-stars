from .client import *

def create_download_filename(filename):
    basename = os.path.basename(filename)
    return f'with-new-wcs-{basename}'

def make_arguments_for_astrometry_client(filename=None, apikey=None):
    '''
    This feels real kludgy, but....

    This will make a kludged sys.argv
    to pass to our slightly kludged version
    of the astrometry.net client.py,
    so that we can use its argument-parsing.
    '''

    argv = ['client.py']

    # add the API key
    argv.append( f'--apikey={apikey}')

    # add the upload filename
    argv.append( f'--upload={filename}')

    # add the download filename
    new_filename = create_download_filename(filename)
    argv.append( f'--newfits={new_filename}')

    return argv

def make_sure_we_have_api_key(apikey=None):
    best_apikey = apikey or os.getenv('AN_API_KEY')
    if best_apikey is None:
        print('''
Alas, it looks like you have no API key defined for using astrometry.net,
so we can't submit images for it to try to plate-solved.

Please visit http://nova.astrometry.net/api_help to find your API key
and then enter it in the prompt below.

You can avoid this step in the future by
    1) defining a system-wide variable AN_API_KEY='...' (for example, in your .bash_profile or .zprofile on Macs),
    or
    2) passing the keyword argument apikey='...' to your Python function call
        ''')
        best_apikey = input('Please enter your astrometry.net API key here:\n')
    return best_apikey

def find_WCS(filename=None, apikey=None):
    apikey = make_sure_we_have_api_key(apikey)
    argv = make_arguments_for_astrometry_client(filename=filename, apikey=apikey)
    print(f'''

    Sending your image {filename}
    away to be processed by astrometry.net.
    This may take up to a few minutes.

    ''')
    run_astrometry_dot_net(argv)
    new_filename = create_download_filename(filename)
    print(f'''

    Your image, with its updated WCS,
    has been downloaded to
    {new_filename}

    ''')
    return new_filename
