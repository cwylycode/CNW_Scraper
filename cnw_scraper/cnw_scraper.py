"""
Author: hexadeci-male
Version: I dunno LOL

Celebrity Net Worth website scraper - Scrapes profile data from people and things you specify (or generalize).

Purpose: Scrape celebritynetworth.com and compile the profile data of celebrities, businessmen, companies, etc. so they can be used for data aggregation. What you use the data for is ultimately up to you. You could parse the data into CSV/JSON/WHATEVER and save the files, you could sort and present it through pandas and matplotlib, or you could simply print out and display the profile data directly and cry at how poor you are compared to all of them. Also, you can periodically call the functions to get new versions of the profiles when and if they get updated in the future.

Usage: Use the scrape_* functions to collect the profile data the way you want. Each function essentially visits the site through URLs, parses the profiles and collects the data it finds and returns it through profile objects. Site URLs are handled asynchronously, which means you don't have to wait for one page to finish before the program moves onto the next - all pages get downloaded at the same time and then parsed sequentially once they all arrive. If you have connection problems, or if their servers decide they no longer like you, then the appropriate error gets thrown, the app crashes, the data currently collected gets dropped and you'll have to restart. This shouldn't ever be a problem, though, and the error will most likely be on your end. The site boasts tens of thousands of profiles and, even when getting everything with scrape_all and with the included descriptions, the returned data shouldn't lead to memory errors.

Options: This program uses print logs to show the stages of what's happening when you call a function - change opt_silence_logs to true to prevent logging. You can also change the user-agent for the client connection to something else through opt_custom_user_agent. Finally, change opt_include_description to false if you don't want your profiles to include the description portion (which can be lengthy and arguably needless for data processing).

There's other stuff from the website you could potentially get, such as trending profiles, couples, articles, home page stuff, etc. They aren't implemented in this scraper because at that point you may as well just visit the website anyway. Fun fact: if you look on the site map XML for CNW, you'll find a directory for the maps section and inside you'll see that there's waaay more locations to choose from than the ones listed here in the Location Enum.
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup,SoupStrainer
from enum import Enum
from os import name as _osname

# ----------Setup & Initialize

opt_custom_user_agent = ""
opt_include_description = True
opt_silence_logs = False
_DEFAULT_UA = "Totally Not A Bot"
_PARSER = "html.parser"
_TIMEOUT = aiohttp.ClientTimeout(total=15,connect=10)
if _osname == "nt":
    # Prevents Windows-specific nonsense about "Event loop is closed" with asyncio loop policy
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------- Classes & Enumerations

class Category(Enum):
    """
    Category types found on the site for collecting profiles from different fields.
    """
    ACTORS = "actors"
    ATHLETES = "richest-athletes"
    AUTHORS = "authors"
    BASEBALL = "richest-baseball"
    BILLIONAIRES = "richest-billionaires"
    BOLLYWOOD = "bollywood-celebrities"
    BOXERS = "richest-boxers"
    BUSINESS = "richest-businessmen"
    CELEBRITIES = "richest-celebrities"
    CEOS = "ceos"
    CHEFS = "richest-celebrity-chefs"
    COACHES = "richest-coaches"
    COMEDIANS = "richest-comedians"
    COMPANIES = "companies"
    CRIMINALS = "richest-criminals"
    DJS = "richest-djs"
    DEMOCRATS = "democrats"
    DESIGNERS = "richest-designers"
    DIRECTORS = "directors"
    EXECUTIVES = "business-executives"
    GOLFERS = "richest-golfers"
    HOCKEY = "hockey"
    INTERNATIONAL = "international-celebrities"
    INDIA = "indian-celebrities"
    LAWYERS = "lawyers"
    MMA = "mma-net-worth"
    MODELS = "models"
    NBA = "nba"
    NFL = "nfl"
    OLYMPIANS = "olympians"
    POLITICIANS = "richest-politicians"
    PRESIDENTS = "presidents"
    PRODUCERS = "producers"
    RACERS = "race-car-drivers"
    RAPPERS = "rappers"
    REPUBLICANS = "republicans"
    ROCKSTARS = "rock-stars"
    ROYALS = "royals"
    SHEIKS = "sheiks"
    SINGERS = "singers"
    SKATEBOARDERS = "skateboarders"
    SOCCER = "richest-soccer"
    TENNIS = "richest-tennis"
    WALLSTREETERS = "wall-street"
    WRESTLERS = "wrestlers"

class Location(Enum):
    """
    Enumerations of locations provided by the site's map section. Used exclusively by the scrape_map function.
    """
    AFRICA = "africa"
    ASIA = "asia"
    AUSTRALIA = "australia"
    CANADA = "canada"
    CARIBBEAN = "caribbean"
    CENTRALAMERICA = "centralamerica"
    EUROPE = "europe"
    GREENLAND = "greenland"
    ICELAND = "iceland"
    INDIA = "india"
    MEXICO = "mexico"
    MIDDLEEAST = "middleeast"
    RUSSIA = "russia"
    SOUTHAMERICA = "southamerica"
    USA = "united-states"

class _Profile:
    """
    Contains information from a subject's net worth page (print me for a pretty display of my contents).\n
    :stats: Dictionary containing name, net worth, salary, gender, nationality, etc. - Net Worth gets printed out as a dollar amount, but is actually stored as a real number string.\n
    :description: String containing the bio of the subject - optional.\n
    Note: Certain stats for certain profiles might not exist, as the profile simply doesn't have them on the site. A profile will always have at least a name and net worth.
    """
    def __init__(self, stats:dict, description:str):
        self.stats = stats
        self.description = description
    def __str__(self):
        stats = dict(self.stats)
        stats["Net Worth"] = f"${int(stats['Net Worth']):,}"
        x = "".join([f"{key}: {value}\n" for key,value in stats.items()])
        y = self.description[:199]+" ..." if len(self.description) > 200 else self.description
        return x+"Description: "+y

# ---------- Base Functionality

def _log(txt):
    # Used for printing status updates and logging for the application
    if opt_silence_logs: return
    print("CNW - "+txt)

def _parse_profile(page_html):
    # Parse the HTML soup on the profile's page and return the data as a Profile object
    _log("Parsing HTML ...")
    soup = BeautifulSoup(page_html,features=_PARSER,parse_only=SoupStrainer(attrs={"id":"single__main"}))
    soup_name = soup.find(attrs={"itemprop":"name"})["content"]
    soup_stats = soup.find("table",attrs={"class":"celeb_stats_table"})
    soup_desc = soup.find(attrs={"itemprop":"description"})
    # Get name first...
    data = {"Name":soup_name}
    # Then get the rest from the table
    for table in soup_stats:
        data.update({table.td.text[:-1]:table.td.next_sibling.text})
    # Change Net Worth to the numerical representation found on the site
    data["Net Worth"] = soup.find("meta",attrs={"itemprop":"price"})["content"]
    # Get description if wanted
    desc = []
    if opt_include_description:
        for tag in soup_desc.children:
            if tag.name in ["div","img","table","style"]:
                # Junk
                continue
            if tag.name in ["ul","ol"]:
                # Go through lists and collect info within
                for li in tag: desc.append(li.text+'\n\n')
                continue
            desc.append(tag.text+'\n\n')
        desc = "".join(desc)
    else: desc = ""
    _log(f"Compiling profile of '{data['Name']}' ...")
    return _Profile(data, desc)

async def _fetch(url,session):
    try:
        # Get info and payload from a valid URL
        async with session.request(method="GET", url=url, timeout=_TIMEOUT) as response:
            html = await response.text()
            status = response.status
            data = {"status":status,"url":url,"html":html}
    except Exception as err:
        # Kill program if we have a connection error
        await asyncio.sleep(0.5)
        raise err
    _log(f"Fetched page: '{data['status']}' - {data['url']}")
    return data

async def _client(urls):
    # Asynchronously get the requested pages and return list of multiple page HTML responses
    ua = opt_custom_user_agent if opt_custom_user_agent else _DEFAULT_UA
    async with aiohttp.ClientSession(headers={"user-agent":ua}) as session:
        tasks = [_fetch(url,session) for url in urls]
        page_list = await asyncio.gather(*tasks)
    await asyncio.sleep(0.5) # Graceful shutdown of client connections is needed
    return page_list

def _get_pages(urls):
    # Initialize an async client run to connect to site and collect the HTML data from the supplied URLs
    _log(f"Getting ({len(urls)}) page(s) ...")
    pages = asyncio.run(_client(urls))
    _log("Compiling page list ...")
    return list(pages)

def _get_profiles_from_list_in_page(base_page,target_id):
    # Run page through soup and get each listed profile URL inside it
    profile_list = BeautifulSoup(base_page,features=_PARSER,parse_only=SoupStrainer(attrs={"id":target_id}))
    if not profile_list:
        _log("No Profiles found!")
        return []
    profile_urls = [a["href"] for a in profile_list.select("a")]
    # Get profiles from URLs
    profile_pages = _get_pages(profile_urls)
    profiles = [_parse_profile(page["html"]) for page in profile_pages]
    return profiles

def _sort_profiles(profiles,sort_by,sort_ascending):
    if sort_by and sort_by in ["name","worth"]:
        # Key to sort by either profile name or net worth
        k = lambda x: x.stats["Name"] if sort_by == "name" else int(x.stats["Net Worth"])
        _log(f"Sorting Profiles by {sort_by.capitalize()} ({'Ascending' if sort_ascending else 'Descending'}) ...")
        profiles = sorted(profiles,key=k,reverse=not sort_ascending)
    return profiles

# ---------- Main API

def scrape_all(sort_by:str="",sort_ascending:bool=True):
    """
    Make the website sweat! They knew what they were getting themselves into when they decided to fawn over the rich and famous. Long live the proletariat!\n
    This is mostly just a joke function. Specifically, it's a generator that acts as a handle for the scrape_category function, essentially, that gets all available profiles as a result. It calls scrape_category on every category and collects all the profiles for them, yielding one category's worth of profiles at a time. It's basically the same thing as if you yourself were to call scrape_category for every category inside of a loop.\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A generator.
    """
    _log("Starting All function ...")
    for cat in Category:
        profiles = scrape_category(cat,1,-1,sort_by,sort_ascending)
        _log("Profiles compilation finished ...")
        profiles = _sort_profiles(profiles,sort_by,sort_ascending)
        yield profiles
    # Wrap up
    _log("All function finished.")

def scrape_category(category:Category,starting_page:int=1,additional_pages:int=0,sort_by:str="",sort_ascending:bool=True):
    """
    Get the profiles from a category within a page range. Pages are scraped from the very start of the starting page, all the way to the very last profile on the last additional page. By default, get only the profiles from the first page of the category.\n
    :category: Enum from Category class to use. E.g. - category = Category.AUTHORS\n
    :starting_page: The page to start scraping (>0). If page is out of range with category, a page exception is thrown.\n
    :additional_pages: How many more pages to scrape after the starting_page. 0 is default and means no pages after. <0 means all valid pages after. If value is higher than the actual number of available pages, collect all valid pages from starting_page until the end of category.\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A list of Profile objects - optionally sorted.
    """
    _log("Starting Category function ...")
    if not isinstance(category,Category):
        raise Exception("Invalid Category Parameter")
    base_url = "https://www.celebritynetworth.com/category/" + category.value + "/page/"
    _log(f"Getting pages from {category.name} category ...")
    init_page = _get_pages([base_url+str(starting_page)+'/'])[0]
    if init_page["status"] >= 400:
        raise Exception("Starting page is out of range of category.")
    # Get the category pages from start and additional pages
    pages = [init_page]
    count,i = starting_page,1
    while True:
        # Either we get all the pages wanted or we go over and get 404'd, both will end the loop
        if count == starting_page+additional_pages:
            _log(f"Got all requested pages ({i}) ...")
            break
        count += 1
        cat_page = _get_pages([base_url+str(count)+'/'])[0]
        if cat_page["status"] >= 400:
            _log(f"Reached end of category: ({i}) pages collected ...")
            break
        i += 1
        pages.append(cat_page)
    # Got all the valid pages, now parse them of the profile URLs
    _log("Parsing profiles from pages ...")
    profiles = []
    for i,page in enumerate(pages):
        _log(f"Category page {i+1} start ...")
        page_profiles = _get_profiles_from_list_in_page(page["html"],"post_listing")
        profiles.extend(page_profiles)
    # Wrap up
    _log("Profiles compilation finished ...")
    profiles = _sort_profiles(profiles,sort_by,sort_ascending)
    _log("Category function finished.")
    return profiles

def scrape_map(location:Location,sort_by:str="",sort_ascending:bool=True):
    """
    Get the top 100 profiles from a map location on the site.\n
    :location: Enum from Location class to use. E.g. - location = Location.USA\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A list of Profile objects - optionally sorted.
    """
    _log("Starting Map function ...")
    if not isinstance(location,Location):
        raise Exception("Invalid Location Parameter")
    map_url = "https://www.celebritynetworth.com/map/" + location.value + "/"
    _log(f"Getting map page for {location.name} ...")
    html = _get_pages([map_url])[0]["html"]
    _log("Collecting profile URLs from map ...")
    # Get profiles from list inside page
    profiles = _get_profiles_from_list_in_page(html,"cnwMaps_mainProfileList")
    # Wrap up
    _log("Profiles compilation finished ...")
    profiles = _sort_profiles(profiles,sort_by,sort_ascending)
    _log("Map function finished.")
    return profiles

def scrape_names(names:list,sort_by:str="",sort_ascending:bool=True):
    """
    Use the site's search feature to check for each name provided and collect profile data on the subject if the name matches the query.\n
    If a name isn't found, no profile for it will be returned.\n
    Tip: Be sure to not use prefixes (Dr./Mr./Mrs./etc.) or hyphens and use only one space between words - the search engine on the site can be picky. Usually the first/last name is enough to get the right profile. Also, duplicate names are discarded - only one unique profile will be returned per name.\n
    :names: An iterable of strings, with each being the real name (and/or 'stage name') of a person/thing (alphanumeric/spaces only, symbols get stripped). E.g. - ['Elon Musk', 'Apple', 'OPRAH', 'DEADMAU5', 'bill gates', 'Dwayne "The Rock" Johnson', 'The Undertaker']\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A list of Profile objects - optionally sorted.
    """
    _log("Starting Names function ...")
    search_urls = []
    parse_name = lambda n: "".join(filter(lambda x: x.isalnum() or x == " ", n)).strip()
    _log("Creating search URLs ...")
    for name in names:
        # Parse current name for URL query and add to search list - with no duplicate URLs
        query = parse_name(name)
        url = "https://www.celebritynetworth.com/dl/" + query.replace(" ", "-").lower() + "/"
        if url in search_urls: continue
        search_urls.append(url)
    _log("Getting search results ...")
    # Collect the search result pages from the URLs
    results = _get_pages(search_urls)
    # Loop through the resulting search pages and store URL for profile in a list if valid
    profile_urls = []
    for i,page in enumerate(results):
        tag = "post_item anchored  search_result lead"
        lead = BeautifulSoup(page["html"],features=_PARSER,parse_only=SoupStrainer(attrs={"class":tag}))
        if lead:
            # There's a lead search result, check if the contents have our target's name
            current_name = parse_name(names[i])
            txt = lead.text.lower()
            if all([x in txt for x in current_name.lower().split()]):
                # It does - get the target's profile url and 
                _log(f"FOUND: '{current_name}' matches with result.")
                profile_urls.append(lead.find("a")["href"])
            else:
                _log(f"FAILED: '{current_name}' doesn't seem to match search result.\n")
        else:
            _log(f"FAILED: Search for '{current_name}' returned no results.")
    # Get and parse the pages
    _log("Getting matching profiles ...")
    profile_pages = _get_pages(profile_urls)
    profiles = [_parse_profile(page["html"]) for page in profile_pages]
    # Wrap up
    _log("Profiles compilation finished ...")
    profiles = _sort_profiles(profiles,sort_by,sort_ascending)
    _log("Names function finished.")
    return profiles

def scrape_top(category:Category=None,sort_by:str="",sort_ascending:bool=True):
    """
    Get the top 50 richest profiles from a category. If category is left at default (None), get the top 100 overall richest profiles in the world instead.\n
    :category: Enum from Category class to use. E.g. - category = Category.AUTHORS /OR/ category = None = Top 100 list\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A list of Profile objects - optionally sorted.
    """
    _log("Starting Top function ...")
    if category:
        # Check if there's a category and assign the appropriate URL
        if not isinstance(category,Category):
            raise Exception("Invalid Category Parameter")
        top_url = "https://www.celebritynetworth.com/list/top-50-" + category.value + "/"
    else:
        top_url = "https://www.celebritynetworth.com/list/top-100-richest-people-in-the-world/"
    _log(f"Getting toplist page for {category.name if category else 'Top 100'} category ...")
    html = _get_pages([top_url])[0]["html"]
    _log("Collecting profile URLs from list ...")
    # Get profiles from list inside page
    profiles = _get_profiles_from_list_in_page(html,"top_100_list")
    # Wrap up
    _log("Profiles compilation finished ...")
    profiles = _sort_profiles(profiles,sort_by,sort_ascending)
    _log("Top function finished.")
    return profiles

def scrape_random():
    """
    Uses the site's random feature to grab a random profile.\n
    :return: A single Profile object from a randomly chosen subject.
    """
    _log("Starting Random function ...")
    url = "https://www.celebritynetworth.com/random/"
    html = _get_pages([url])[0]["html"]
    profile = _parse_profile(html)
    # Wrap up
    _log("Profile compilation finished ...")
    _log("Random function finished.")
    return profile

if __name__ == "__main__":
    # input("What are you doing here? You're not supposed to run this program by itself. Shoo.")
    profiles = scrape_category(Category.CEOS,1,1,"name")
    print(*profiles[:5],sep='\n\n')