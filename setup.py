from setuptools import setup, find_packages
import pathlib

cwd = pathlib.Path(__file__).parent.resolve()
long_description = (cwd / 'README.md').read_text(encoding='utf-8')

setup(name='sounding_selection',
      version='1.0.0',
      description='Label-Based Method for Hydrographic Sounding Selection',
      license='MIT',
      long_description=long_description,
      author='Noel Dyer',
      package_dir={'': 'src'},
      packages=['sounding_selection'],
      install_requires=['triangle',
                        'numpy==1.21.5',
                        'shapely==1.8.0'],
      python_requires='>=3.6, <4',
      url='https://github.com/NoelDyer/Sounding-Selection',
      long_description_content_type='text/markdown',
      zip_safe=True,
      entry_points={'console_scripts':
                     ['sounding_selection=sounding_selection.main:main']}
      )