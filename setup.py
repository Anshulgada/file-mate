# setup.py
from setuptools import setup, find_packages
import os


def get_long_description():
    with open(
        os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8"
    ) as f:
        return f.read()


setup(
    name="file-mate",
    version="0.1.1",
    description="A command-line tool for image, pdf, and other file manipulations.",
    author="Anshul Gada",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "pypdf",
        "click",
        "reportlab",
        "setuptools",
        "python-magic; platform_system != 'Windows'",  # For Linux/macOS
        "python-magic-bin; platform_system == 'Windows'",  # For Windows
    ],
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "file-mate=file_mate.cli:cli",
        ],
    },
    python_requires=">=3.8",
    package_data={
        "file_mate": ["tests/*"],
    },
)
