# read the contents of your README file
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-setty',

    version='3.1.0',

    author='Michael England',
    author_email='michael.k.england@gmail.com',

    license='Apache License Version 2.0',

    packages=['setty', 'setty.migrations'],
    include_package_data=True,

    url='https://github.com/mikeengland/django-setty',

    description='Django app allowing users to configure settings dynamically in the Admin screen',
    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords='django dynamic live settings setty django-setty admin cache',

    install_requires=['django-picklefield', 'python-memcached'],
    test_suite='setty.tests',
)
