import os
from setuptools import setup, find_packages
from setuptools.command.test import test

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class Test(test):
    user_options = [
        ('test-labels=', 'l', "Test labels to pass to runner.py test"),
        ('djtest-args=', 'a', "Arguments to pass to runner.py test"),
    ]

    def initialize_options(self):
        test.initialize_options(self)
        self.test_labels = 'tests'
        self.djtest_args = ''

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        from tests.runner import main

        test_labels = self.test_labels.split()
        djtest_args = self.djtest_args.split()
        main(['runner.py', 'test'] + test_labels + djtest_args)


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
        "Topic :: Utilities", "License :: OSI Approved :: BSD License",
    ],

    install_requires=[
        "django==1.8.8",
        "celery",
        "djangorestframework>=3",
        "djangorestframework-filters==0.4.0",
        "github3.py<0.9.4",
        "pytz",
    ],

    tests_require=[
        'django_webtest',
        'factory_boy',
        'fake-factory',
    ],

    cmdclass={
        'test': Test,
    },
)
