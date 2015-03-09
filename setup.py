from setuptools import setup, find_packages

setup(
    name='mdapi',
    version='0.1',
    packages=['mdapi'],
    url='http://github.com/areku/mdapi',
    license='GPLv3',
    author='Alexander Weigl',
    author_email='uiduw@student.kit.edu',
    description='',
    install_requires = ["path.py", "jinja2", "click", "sphinx", "sphinxcontrib-napoleon"]
)


