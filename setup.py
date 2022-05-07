import setuptools

setuptools.setup(
    name='ftcli',
    version='0.7.0',
    description='ftCLI',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['ftcli=ftcli.ftcli:main']},
    install_requires=[
        'fonttools==4.33.3',
        'brotli==1.0.9',
        'click==8.1.3',
        'colorama==0.4.4',
        'dehinter==4.0.0',
        'font-line==3.1.4',
        'pathvalidate==2.5.0',
        'skia-pathops==0.7.2',
        'zopfli>=0.1.9',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    zip_safe=False
)
