######################################################################
# Config
interesting_exif_tags = ['Model',
                         'ExposureTime',
                         'ISOSpeedRatings',
                         'FocalLengthIn35mmFilm',
                         'FNumber',
                         'ExifImageWidth',
                         'ExifImageHeight']

######################################################################
# Parse the config
import configparser

config = configparser.ConfigParser()
config.read('uti.cfg')

client_id = config['UTI']['client_id']
client_secret = config['UTI']['client_secret']

######################################################################
# Parse the args
import argparse

parser = argparse.ArgumentParser(description='Upload To Imgur')
parser.add_argument('-a', '--album', help='album ID',
                    default=None)
parser.add_argument('files', metavar='FILE', nargs='+',
                    help='files to upload')
args = parser.parse_args()
files = args.files
album = args.album

######################################################################
# Do the auth
import imgurpython
import sys

client = imgurpython.ImgurClient(client_id, client_secret)
authorization_url = client.get_auth_url('pin')

print('Go to the following URL:')
print('https://api.imgur.com/oauth2/authorize?client_id=df414c6e3144c85&response_type=pin')
pin=input('And type the pin: ')

try:
    credentials = client.authorize(pin, 'pin')
    client.set_user_auth(credentials['access_token'],
                         credentials['refresh_token'])
except:
    print('Authentication error.')
    sys.exit(-1)

creds=client.get_credits()
    
######################################################################
# Read Exif and Upload file
import PIL.Image
import PIL.ExifTags
import datetime
from imgurpython.helpers.error import ImgurClientError
print('files:')
for f in files:
    print('=== file: {}'.format(f))
    # Check credits
    print('user credits:   {}/{}'.format(
        creds['UserRemaining'], creds['UserLimit']))
    print('client credits: {}/{}'.format(
        creds['ClientRemaining'], creds['ClientLimit']))
    print('reset:          {}'.format(
        datetime.datetime.fromtimestamp(int(creds['UserReset']))))
    if int(creds['UserRemaining']) < 10 or int(creds['ClientRemaining']) < 10:
        print('Insufficient credits.  Try again later.')
        sys.exit(0)
    img = PIL.Image.open(f)
    exif = {
        PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
    }
    # hacks so the data looks nice
    exif['ExposureTime'] = '1/{}'.format(
        exif['ExposureTime'][1]//exif['ExposureTime'][0])
    exif['FNumber'] = exif['FNumber'][0]//exif['FNumber'][1]
    config = { 'album' : album, 'description' : ''}
    for k in interesting_exif_tags:
        config['description'] += '{} : {}\n'.format(k, exif[k])
    done=False
    err=None
    print('Uploading', end='', flush=True)
    while not done:
        try:
            print('.', end='', flush=True)
            image=client.upload_from_path(f, config=config, anon=False)
            creds=client.credits
            done=True
            print('success!')
        except imgurpython.helpers.error.ImgurClientRateLimitError:
            print('Rate limit exceeded, try again tomorrow.')
            sys.exit(-2)
        except KeyboardInterrupt:
            if err != None:
                print('The last error was: {}'.format(e))
            sys.exit(-1)
        except:
            err = sys.exc_info()[0]
            print('e', end='', flush=True)
