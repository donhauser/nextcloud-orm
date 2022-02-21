import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='nextcloud-orm',
    version='0.0.1',
    description='A simple object relation model (ORM) wrapper for the nextcloud api (ocs)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jonas Donhauser',
    #author_email='',
    url='https://github.com/donhauser/nextcloud-orm',
    packages=['nextcloud_orm'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["nextcloud-api-wrapper>=0.2.1.5"],
)
