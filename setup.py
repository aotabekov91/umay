from setuptools import setup, find_packages

setup(name="umay",
      version="0.0.1",
      description="Umay",
      packages=find_packages(),
      install_requires=[
          'plug==0.0.1',
          'pyzmq==25.0.2', 
          ],
      extras_require={
          'snips_nlu': [
              'setuptools-rust',
              'cython',
              'snips_nlu', 
              'numpy==1.20.0'
              ]
          },
      include_package_data=True,
      package_data={'':['*', '*/*', '*/*/*', '*/*/*/*']},
      entry_points = {
          'console_scripts': [
              'umay = umay.run:main',
              ]
          },
      )
