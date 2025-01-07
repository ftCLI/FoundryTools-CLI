import setuptools

from pathlib import Path

this_directory = Path(__file__).parent
long_description = this_directory.joinpath("README.md").read_text()


def _get_requirements() -> list[str]:
    """
    Relax hard pinning in setup.py
    """
    with open("requirements.txt", encoding="utf-8") as requirements:
        return [line.replace("==", ">=") for line in requirements.readlines()]


setuptools.setup(
    name="foundrytools-cli",
    version="2.0.0",
    description="A set of command line tools to inspect, manipulate and convert font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ftCLI",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/FoundryTools-CLI",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["ftcli = foundrytools_cli.__main__:cli"]},
    install_requires=_get_requirements(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Text Processing :: Fonts",
    ],
    python_requires=">=3.9",
    zip_safe=False,
)
