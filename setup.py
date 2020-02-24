from setuptools import setup

try:
    with open("Readme.md", "r") as fh:
        long_description = fh.read()
except IOError:
    long_description = ""  # sorry

setup(
    name = "pynwjs",
    version = "0.0.3",
    author = "Philipp Schillinger",
    author_email = "schillin@kth.se",
    description = "Use nwjs as GUI in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license = "BSD 3",
    url = "https://github.com/pschillinger/pynwjs",
    package_dir = {'': 'src'},
    packages=['pynwjs'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
    ]
)
