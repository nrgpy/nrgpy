from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
      name='nrgpy',
      version='0.13.1',
      description='library for handling NRG Systems data files',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/nrgpy/nrgpy',
      author='NRG Systems, Inc.',
      author_email='support@nrgsystems.com',
      keywords='nrg systems rld symphonie symphoniepro wind data spidar remote sensor lidar',
      packages=[
            'nrgpy'
      ],
      install_requires=[
            'pandas>=0.23',
            'requests',
      ],
      python_requires='>=3.0',
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ]
)
