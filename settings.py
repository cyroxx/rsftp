# heahdk.net
BASE_URI = 'https://heahdk.net/storage/cyroxx/public/'
ACCESS_TOKEN = ''

# 5apps
#BASE_URI = 'https://storage.5apps.com/cyroxx/public/'
#ACCESS_TOKEN = '<your_access_token>'

# You better should provide ACCESS_TOKEN from local_settings.py,
# which is not version-controlled.
try:
    from local_settings import *
except ImportError:
    pass
