try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'mapthingi',
    'author': 'Theresa Csar, Christian Knapp, Michael Emhofer, Florian Holzner',
    'url': 'https://github.com/theresacsar/mapthingi',
    'download_url': 'https://github.com/theresacsar/mapthingi',
    'author_email': 'th.csar@gmail.com, , , hallo@lebobs.ch',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['stlwriter'],
    'scripts': [],
    'name': 'mapthingi'
}

setup(**config)