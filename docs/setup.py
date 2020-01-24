from setuptools import setup

setup(
      name='nrgpy_docs',
      version='0.0.1',
      description='nrgpy formatting for readthedocs',
      url='https://github.com/nrgpy/nrgpy',
      author='NRG Systems, Inc.',
      author_email='support@nrgsystems.com',
      keywords='nrg systems rld symphonie symphoniepro wind data spidar remote sensor lidar',
      packages=[
            'nrgpy_docs'
      ],
      install_requires=[
            'sphinx',
      ],
      python_requires='>=3.0',
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ]
)
