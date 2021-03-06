from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages

import sys
import codecs
import os
import platform
import re


###############################################################################

NAME = "argon2_cffi"
PACKAGES = find_packages(where="src")

CFFI_MODULES = ["src/argon2/_ffi_build.py:ffi"]
lib_base = os.path.join("extras", "libargon2", "src")
include_dirs = [
    os.path.join(lib_base, "..", "include"),
    os.path.join(lib_base, "blake2"),
]

# Add vendored integer types headers if necessary.
is_windows = "win32" in str(sys.platform).lower()
if is_windows:
    int_base = "extras/msinttypes/"
    inttypes = int_base + "inttypes"
    stdint = int_base + "stdint"
    vi = sys.version_info[0:2]
    if vi in [(2, 6), (2, 7)]:
        # VS 2008 needs both.
        include_dirs += [inttypes, stdint]
    elif vi in [(3, 3), (3, 4)]:
        # VS 2010 needs inttypes.h and fails with both.
        include_dirs += [inttypes]

# Optimized version requires SSE2 extensions.  They have been around since
# 2001 so we try to compile it on every recent-ish x86.
optimized = platform.machine() in ("i686", "x86", "x86_64", "AMD64")

LIBRARIES = [
    ("libargon2", {
        "include_dirs": include_dirs,
        "sources": [
            os.path.join(lib_base, path)
            for path in [
                "argon2.c",
                os.path.join("blake2", "blake2b.c"),
                "core.c",
                "encoding.c",
                "opt.c" if optimized else "ref.c",
                "thread.c",
            ]
        ],
    }),
]
META_PATH = ("src", "argon2", "__init__.py")
KEYWORDS = ["password", "hash", "hashing", "security"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python",
    "Topic :: Security :: Cryptography",
    "Topic :: Security",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

SETUP_REQUIRES = ["cffi"]
if is_windows and sys.version_info[0] == 2:
    # required for "Microsoft Visual C++ Compiler for Python 2.7"
    # https://www.microsoft.com/en-us/download/details.aspx?id=44266
    SETUP_REQUIRES.append("setuptools>=6.0")

INSTALL_REQUIRES = ["six", "cffi>=1.0.0"]
# we're not building universal wheel so this works.
if sys.version_info[0:2] < (3, 4):
    INSTALL_REQUIRES += ["enum34"]

EXTRAS_REQUIRE = {}

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(*META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


URI = find_meta("uri")
LONG = (
    read("README.rst") + "\n\n" +
    "Release Information\n" +
    "===================\n\n" +
    re.search("(\d+.\d.\d \(.*?\)\n.*?)\n\n\n----\n\n\n",
              read("CHANGELOG.rst"), re.S).group(1) +
    "\n\n`Full changelog " +
    "<{uri}en/stable/changelog.html>`_.\n\n".format(uri=URI) +
    read("AUTHORS.rst")
)


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=URI,
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        long_description=LONG,
        keywords=KEYWORDS,
        packages=PACKAGES,
        package_dir={"": "src"},
        cffi_modules=CFFI_MODULES,
        ext_package="argon2",
        libraries=LIBRARIES,
        zip_safe=False,
        classifiers=CLASSIFIERS,
        setup_requires=SETUP_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
    )
