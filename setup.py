from pathlib import Path
import re

from setuptools import find_packages, setup


ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
INIT_FILE = ROOT / "src" / "foundrytools_cli" / "__init__.py"

match = re.search(r'__version__\s*=\s*"([^"]+)"', INIT_FILE.read_text(encoding="utf-8"))
if not match:
    raise RuntimeError("Unable to find package version in src/foundrytools_cli/__init__.py")

setup(
    name="foundrytools-cli",
    version=match.group(1),
    description="A set of command line tools to inspect, manipulate and convert font files",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Cesare Gilento",
    author_email="ftcli@proton.me",
    license="MIT",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "afdko>=4.0.3",
        "click>=8.3.1",
        "foundrytools>=0.1.6",
        "loguru>=0.7.3",
        "pathvalidate>=3.3.1",
        "rich>=14.3.3",
        "ufolib2>=0.18.1",
        "win32-setctime>=1.2.0; sys_platform == 'win32'",
    ],
    extras_require={
        "dev": [
            "bump-my-version>=1.2.7",
            "mypy>=1.19.1",
            "pre-commit>=4.5.1",
            "pylint>=4.0.5",
        ],
        "docs": [
            "sphinx-click>=6.2.0",
            "sphinx-rtd-theme>=3.1.0",
        ],
    },
    entry_points={"console_scripts": ["ftcli=foundrytools_cli.__main__:cli"]},
    project_urls={
        "Homepage": "https://github.com/ftCLI/FoundryTools-CLI",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Fonts",
    ],
)
