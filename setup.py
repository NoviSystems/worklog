import os
from setuptools import setup, find_packages

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Worklog",
    version="0.8",
    author="Brian Bouterse",
    author_email="bmbouter@gmail.com",
    description=("A Django based, hourly work logging app which supports job coding, view filtering, csv report generation and an e-mail reminder system"),
    keywords="Work logging, Report, Email reminder",
    url="https://www.fi.ncsu.edu/",
    long_description=read('README.md'),
    packages=find_packages(),  
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities","License :: OSI Approved :: BSD License", 
    ],
    install_requires=[
        "celery",
        "djangorestframework",
        "xhtml2pdf",
        "reportlab==2.7",
        "pisa",
        "pytz",
        "south",
    ],
)
