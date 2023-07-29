from setuptools import setup, find_packages

setup(name="umay",
      version="0.0.1",
      description="Umay",
      packages=find_packages(),
      include_package_data=True,
      package_data={'':['*', '*/*', '*/*/*', '*/*/*/*']},
      entry_points = {'console_scripts': ['umay = umay.run:main']},
      )
