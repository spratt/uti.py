import configparser

config = configparser.ConfigParser()
config.read('uti.cfg')

client_id = config['UTI']['client_id']
client_secret = config['UTI']['client_secret']

from imgurpython import ImgurClient

client = ImgurClient(client_id, client_secret)

# Authorization flow, pin example (see docs for other auth types)
authorization_url = client.get_auth_url('pin')

print('Go to the following URL:')
print('https://api.imgur.com/oauth2/authorize?client_id=df414c6e3144c85&response_type=pin')
pin=input('And type the pin: ')

print('pin:           {}'.format(pin))
print('client_id:     {}'.format(client_id))
print('client_secret: {}'.format(client_secret))

#credentials = client.authorize('PIN OBTAINED FROM AUTHORIZATION', 'pin')
#client.set_user_auth(credentials['access_token'], credentials['refresh_token'])
