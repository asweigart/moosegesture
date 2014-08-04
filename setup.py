
from setuptools import setup


# Dynamically calculate the version based on pygcurse.VERSION.
version = __import__('moosegesture').__version__


setup(
    name='MooseGesture',
    version=version,
    url='https://github.com/asweigart/moosegesture',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('A mouse gesture recognition module for Python.'),
    license='BSD',
    packages=['moosegesture'],
    test_suite='tests',
    keywords="mouse gesture",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)