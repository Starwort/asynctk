from distutils.core import setup

with open("README.md") as file:
    long_desc = file.read()

setup(
    name="asynctk",
    version="0.0.1a",
    author="Starwort",
    description="An asynchronous wrapper for TK/TCL using TKInter and AsyncIO",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    packages=["asynctk"],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU GPL 3.0",
        "Operating System :: OS Independent",
    ],
    install_requires=["asyncio"],
    download_url = 'https://github.com/Starwort/asynctk'
)
