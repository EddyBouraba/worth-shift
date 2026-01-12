"""
Setup configuration pour le package shift_comparator
"""
from setuptools import setup, find_packages

setup(
    name="shift-comparator",
    version="1.0.0",
    description="Comparateur de remplacements 3x8",
    author="Worth Shift Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "gunicorn==21.2.0",
    ],
    include_package_data=True,
    package_data={
        "shift_comparator.web": ["static/*"],
    },
)
