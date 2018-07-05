from setuptools import setup
setup(
    name='scryunix',
    packages=['scryunix'],
    version='1.0',
    description='A simple terminal tool to fetch MTG card info',
    author='Mendess2526',
    author_email='pedro.mendes.26@gmail.com',
    url='https://github.com/Mendess2526/scryunix',
    download_url='https://github.com/Mendess2526/scryunix/archive/scry.zip',
    keywords=['mtg', 'card', 'fetch', 'search', 'terminal', 'unix'],
    install_requires=[
        'scrython',
        'termcolor'
    ],
    scripts=['scry/scryunix']
)