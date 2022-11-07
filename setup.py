from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nrgpy',
    version="1.8.4",
    description='library for handling NRG Systems data files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nrgpy/nrgpy',
    author='NRG Systems, Inc.',
    author_email='support@nrgsystems.com',
    keywords='nrg systems rld symphonie symphoniepro wind data spidar remote sensor lidar',
    packages=[
        'nrgpy',
        'nrgpy.api',
        'nrgpy.cloud_api',
        'nrgpy.convert',
        'nrgpy.quality',
        'nrgpy.read',
        'nrgpy.utils',
    ],
    install_requires=[
        'pandas>=1.0',
        'psutil',
        'requests',
    ],
    python_requires='>=3.6',
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ]
)
