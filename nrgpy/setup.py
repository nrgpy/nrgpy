from setuptools import setup

setup(name='nrgpy',
      version='0.1',
      description='library for handling NRG SymphoniePRO Data Logger files',
      url='https://tzotsi@bitbucket.org/tzotsi/nrgpy.git',
      author='NRG Technical Services',
      author_email='support@nrgsystems.com',
      license='MIT',
      keywords='nrg systems rld symphonie symphoniepro',
      packages=[
            'sympro_txt',
            'convert_rld',
      ],
      install_requires=[
            'pandas',
            'pyarrow',
      ],
      zip_safe=False)