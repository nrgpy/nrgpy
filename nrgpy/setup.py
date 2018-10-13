from setuptools import setup

setup(name='nrgpy',
      version='0.1.0',
      description='library for handling NRG Systems data files',
      url='',
      author='NRG Systems, Inc.',
      author_email='support@nrgsystems.com',
      license='MIT',
      keywords='nrg systems rld symphonie symphoniepro',
      packages=[
            'nrgpy'
      ],
      install_requires=[
            'pandas>=0.23',
            'pyarrow',
      ],
      zip_safe=False)
