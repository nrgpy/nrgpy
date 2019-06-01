from setuptools import setup

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(
      name='nrgpy',
      version='0.5.0',
      description='library for handling NRG Systems data files',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/nrgpy/nrgpy',
      author='NRG Systems, Inc.',
      author_email='support@nrgsystems.com',
      keywords='nrg systems rld symphonie symphoniepro wind data',
      packages=[
            'nrgpy'
      ],
      install_requires=[
            'nrgmodbus',
            'pandas>=0.23',
            'pyodbc',
            'requests',
      ],
      python_requires='>=3.0',
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ]
)
