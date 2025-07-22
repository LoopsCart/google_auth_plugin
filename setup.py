from setuptools import find_packages, setup

setup(
    name="google_auth_plugin",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    description="A reusable Django app for social authentication.",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)
