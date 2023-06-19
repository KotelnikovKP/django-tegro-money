from setuptools import setup
from os import path

from django_tegro_money import get_version

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name='django-tegro-money',
    version=get_version(),
    description='Django Tegro.Money HTTP API Connector',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KotelnikovKP/django-tegro-money",
    license="MIT License",
    author="Konstantin Kotelnikov",
    author_email="kotelnikov1302@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
    ],
    keywords="tegro money api connector",
    packages=["django_tegro_money", ],
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "django",
    ],
)
