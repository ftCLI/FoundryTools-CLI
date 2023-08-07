import setuptools

from pathlib import Path

this_directory = Path(__file__).parent
long_description = this_directory.joinpath("README.md").read_text()

setuptools.setup(
    name="foundrytools-cli",
    version="1.0.2.1",
    description="A set of command line tools to inspect, manipulate and convert font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ftCLI",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/FoundryTools-CLI",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["ftcli = foundryToolsCLI.__main__:main"]},
    install_requires=[
        "afdko>=3.9.6",
        "fonttools>=4.42.0",
        "beziers>=0.5.0",
        "brotli>=1.0.9",
        "click>=8.1.6",
        "cffsubr>=0.2.9.post1",
        "dehinter>=4.0.0",
        "pathvalidate>=3.1.0",
        "psautohint>=2.4.0",
        "rich>=13.5.2",
        "skia-pathops>=0.7.4",
        "ttfautohint-py>=0.5.1",
        "zopfli>=0.2.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    zip_safe=False,
)
