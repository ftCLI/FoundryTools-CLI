import setuptools

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="font-CLI",
    version="0.9.11",
    description="A set of command line tools to edit fonts with FontTools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ftCLI",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/ftCLI",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["ftcli=ftCLI.ftCLI:main"]},
    install_requires=[
        "fonttools>=4.39.3",
        "afdko==3.9.5",
        "beziers==0.5.0",
        "brotli==1.0.9",
        "click==8.1.3",
        "dehinter==4.0.0",
        "pathvalidate==2.5.2",
        "rich>=13.3.5",
        "skia-pathops==0.7.4",
        "ttfautohint-py==0.5.1",
        "ufo2ft==2.31.1",
        "zopfli==0.2.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7, <3.11",
    zip_safe=False,
)
