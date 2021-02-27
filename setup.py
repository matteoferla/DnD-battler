from setuptools import setup, find_packages
import sys, os

if sys.version_info.major != 3 or sys.version_info.minor < 6:
    print(sys.version_info)
    raise SystemError('Module written for Python 3.6+.')

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    __doc__ = f.read()
description = __doc__.split('\n')[1] # non-title line.


setup(
    name='DnD-battler',
    version='0.2',
    python_requires='>3.6',
    packages=find_packages(),
    package_data={'': ['beastiary.csv']},
    include_package_data=True,
    url='https://github.com/matteoferla/DnD-battler',
    license='MIT',
    author='matteoferla',
    author_email='matteo.ferla@gmail.com',
    description=description,
    long_description=__doc__,
    long_description_content_type='text/markdown',
)
