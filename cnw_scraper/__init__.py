__version__ = "1.0.2"
__doc__="""
Celebrity Net Worth website scraper
===================================
Scrapes profile data from people and things on the website celebritynetworth.com that you specify (or generalize).

Purpose
-------
Scrape celebritynetworth.com and compile the profile data of celebrities, businessmen, companies, etc. so they can be used for data aggregation. What you use the data for is ultimately up to you. You could parse the data into CSV/JSON/WHATEVER and save the files, you could sort and present it through pandas and matplotlib, or you could simply print out and display the profile data directly and cry at how poor you are compared to all of them. Also, you can periodically call the functions to get new versions of the profiles when and if they get updated in the future.

Usage
-----
Use the scrape_* functions to collect the profile data the way you want. Each function essentially visits the site through URLs, parses the profiles and collects the data it finds and returns it through Profile objects. Site URLs are handled asynchronously, which means you don't have to wait for one page to finish before the program moves onto the next - all pages get downloaded at the same time and then parsed sequentially once they all arrive. If you have connection problems, or if their servers decide they no longer like you, then the appropriate error gets thrown, the app crashes, the data currently collected gets dropped and you'll have to restart. This shouldn't ever be a problem, though, and the error will most likely be on your end. That said, you can always use try/except statements in your own code to 'retry' the scrape attempts.

Options & Logging
-----------------
This program uses console and file logs to show the stages of what's happening when functions get called - you can change log settings in the Log class. You can also change miscellaneous options inside the Options class.

ETC...
------
The site boasts tens of thousands of profiles, which can be all collected through using the scrape_category function. There's other stuff from the website you could potentially get, such as trending profiles, couple's info, articles, home page stuff, etc. They aren't implemented in this scraper because at that point you may as well just visit the website anyway. Fun fact: if you look on the site map XML, you'll find a directory for the maps section and inside you'll see that there's waaay more locations to choose from than the ones listed in the Location Enum.
"""

from cnw_scraper.api import(
    scrape_category,
    scrape_map,
    scrape_names,
    scrape_random,
    scrape_top,
)
from cnw_scraper.categories import Category
from cnw_scraper.locations import Location
from cnw_scraper.logs import Logs
from cnw_scraper.options import Options
from cnw_scraper.profile import Profile