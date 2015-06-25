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
from imgurpython import ImgurClient

client = ImgurClient(client_id, client_secret)
authorization_url = client.get_auth_url('pin')

print('Go to the following URL:')
print('https://api.imgur.com/oauth2/authorize?client_id=df414c6e3144c85&response_type=pin')
pin=input('And type the pin: ')

print('pin:           {}'.format(pin))
print('client_id:     {}'.format(client_id))
print('client_secret: {}'.format(client_secret))

credentials = client.authorize(pin, 'pin')
client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

# Read Exif
import PIL.Image
import PIL.ExifTags
print('files:')
for f in files:
    print('\t{}'.format(f))
    img = PIL.Image.open(f)
    exif = {
        PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
    }
    print('\t\tAlbum: {}'.format(album))
    # hacks so the data looks nice
    exif['ExposureTime'] = '1/{}'.format(
        exif['ExposureTime'][1]//exif['ExposureTime'][0])
    exif['FNumber'] = exif['FNumber'][0]//exif['FNumber'][1]
    config = { 'album' : album, 'description' : ''}
    for k in ['Model', 'ExposureTime', 'ISOSpeedRatings',
              'FocalLengthIn35mmFilm', 'FNumber', 'ExifImageWidth',
              'ExifImageHeight']:
        print('\t\t{}: {}'.format(k, exif[k]))
        config['description'] += '{} : {}\n'.format(k, exif[k])
    image = client.upload_from_path(f, config=config, anon=False)
