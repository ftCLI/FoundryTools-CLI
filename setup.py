import setuptools

setuptools.setup(
    name='ftcli',
    version='0.3.3',
    description='ftCLI',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['ftcli=ftcli.ftcli:main']},
    install_requires=[
        'fonttools==4.27.1',
        'brotli==1.0.9',
        'click==8.0.3',
        'colorama==0.4.4',
        'dehinter==3.1.0',
        'font-line==3.1.4',
        'skia-pathops==0.7.1',
        'zopfli==0.1.8',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    zip_safe=False
)
