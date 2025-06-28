from setuptools import setup, find_packages

setup(
    name="haraka",
    version="0.2.53",  # Use your new version
    packages=find_packages(where="haraka"),  # Automatically find all packages in 'haraka'
    install_requires=[
        # General utilities (from the "gen" group)
        "pathspec==0.10.3",
        "PyYAML==6.0.1",  # Adjust to only one version to avoid conflicts
        "wcwidth==0.2.5",

        # PyFast functionality (from the "PyFast" group)
        "fastapi==0.115.14",
    ],
    extras_require={
        # Group for general utilities
        "gen": [
            "pathspec==0.10.3",
            "PyYAML==6.0.1",  # Pick the correct version
            "wcwidth==0.2.5",
        ],
        # Group for PyFast functionality
        "PyFast": [
            "fastapi==0.115.14",
        ],
    },
)
