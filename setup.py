from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='affinitic.sphinxcontrib.sqlalchemy',
      version=version,
      description="Document sqlalchemy mappers",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python"],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['affinitic', 'affinitic.sphinxcontrib'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools']
      )
