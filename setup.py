from setuptools import setup

setup(
    name='django-setty',

    version='1.0.1',

    author='Michael England',
    author_email='michael.k.england@gmail.com',

    license='Apache License Version 2.0',

    packages=['setty'],
    include_package_data=True,

    url='https://github.com/mikeengland/django-setty',

    description='Django app allowing users to configure settings dynamically in the Admin screen',
    long_description='Django Setty is a Django app which allows users to configure settings dynamically '
                     'in the Django Admin console. A number of data types are supported - dicts, lists, '
                     'integers, floats, strings and booleans. Two backends are bundled - one is a database backend '
                     'which uses the database to retrieve the settings, and the other uses Memcached to cache the '
                     'settings defined in the database.',

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

    install_requires=['Django', 'django-picklefield', 'python-memcached'],
    test_suite='setty.tests',
)
