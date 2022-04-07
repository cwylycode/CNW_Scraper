"""
Profile data webscraper for the site celebritynetworth.com
"""

from setuptools import setup

with open("README.md") as f:
    ld = f.read()

setup(
    name="cnw_scraper",
    version="1.0.2",
    description="Scrapes profile data from people and things you specify (or generalize).",
    license="MIT",
    long_description=ld,
    long_description_content_type="text/markdown",
    author="cwylycode",
    url="https://github.com/cwylycode/CNW_Scraper",
    packages=['cnw_scraper'],
    install_requires=[
        "aiohttp==3.7.4.post0",
        "async-timeout==3.0.1",
        "attrs==21.2.0",
        "beautifulsoup4==4.9.3",
        "chardet==4.0.0",
        "idna==3.1",
        "multidict==5.1.0",
        "soupsieve==2.2.1",
        "typing-extensions==3.10.0.0",
        "yarl==1.6.3",
    ],
    python_requires='>=3.8'
)