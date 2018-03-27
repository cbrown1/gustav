# -*- coding: utf-8 -*-

from setuptools import setup
import gustav

setup(name='gustav',
      version=gustav.__version__,
      description=gustav.__doc__,
      author='Christopher Brown',
      author_email='cbrown1@pitt.edu',
      maintainer='Christopher Brown',
      maintainer_email='cbrown1@pitt.edu',
      packages=['gustav', 'gustav.frontends', 'gustav.methods', 'gustav.user_scripts'],
      platforms = ['linux'],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Scientific/Engineering',
        ],
     )
