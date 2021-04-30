# ---------- Main API for the user

import cnw_scraper.base_functions as bf
from cnw_scraper.categories import Category
from cnw_scraper.locations import Location
from cnw_scraper.logs import Logs
from cnw_scraper.options import Options as opt
from bs4 import BeautifulSoup,SoupStrainer

def scrape_all(sort_by:str="",sort_ascending:bool=True):
    """
    Make the website sweat! They knew what they were getting themselves into when they decided to fawn over the rich and famous. Long live the proletariat!\n
    This is mostly just a joke function. Specifically, it's a generator that acts as a handle for the scrape_category function, essentially, that gets all available profiles as a result. It calls scrape_category on every category and collects all the profiles for them, yielding one category's worth of profiles at a time. It's basically the same thing as if you yourself were to call scrape_category for every category inside of a loop.\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A generator.
    """
    Logs._log("Starting All function ...")
    for cat in Category:
        profiles = scrape_category(cat,1,-1,sort_by,sort_ascending)
        Logs._log(f"Compilation of {cat.name} profiles finished ...")
        profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
        yield profiles
    # Wrap up
    Logs._log("All function finished.")

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
    Logs._log("Starting Category function ...")
    if not isinstance(category,Category):
        raise Exception("Invalid Category Parameter")
    base_url = "https://www.celebritynetworth.com/category/" + category.value + "/page/"
    Logs._log(f"Getting pages from {category.name} category ...")
    init_page = bf.get_pages([base_url+str(starting_page)+'/'])[0]
    if init_page["status"] >= 400:
        raise Exception("Starting page is out of range of category.")
    # Get the category pages from start and additional pages
    pages = [init_page]
    count,i = starting_page,1
    while True:
        # Either we get all the pages wanted or we go over and get 404'd, both will end the loop
        if count == starting_page+additional_pages:
            Logs._log(f"Got all requested pages ({i}) ...",True)
            break
        count += 1
        cat_page = bf.get_pages([base_url+str(count)+'/'])[0]
        if cat_page["status"] >= 400:
            Logs._log(f"Reached end of category: ({i}) pages collected ...",True)
            break
        i += 1
        pages.append(cat_page)
    # Got all the valid pages, now parse them of the profile URLs
    Logs._log("Parsing profiles from pages ...")
    profiles = []
    for i,page in enumerate(pages):
        Logs._log(f"Category page {i+1} start ...",True)
        page_profiles = bf.get_profiles_from_list_in_page(page["html"],"post_listing")
        profiles.extend(page_profiles)
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Category function finished.")
    return profiles

def scrape_map(location:Location,sort_by:str="",sort_ascending:bool=True):
    """
    Get the top 100 profiles from a map location on the site.\n
    :location: Enum from Location class to use. E.g. - location = Location.USA\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A list of Profile objects - optionally sorted.
    """
    Logs._log("Starting Map function ...")
    if not isinstance(location,Location):
        raise Exception("Invalid Location Parameter")
    map_url = "https://www.celebritynetworth.com/map/" + location.value + "/"
    Logs._log(f"Getting map page for {location.name} ...")
    html = bf.get_pages([map_url])[0]["html"]
    Logs._log("Collecting profile URLs from map ...")
    # Get profiles from list inside page
    profiles = bf.get_profiles_from_list_in_page(html,"cnwMaps_mainProfileList")
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Map function finished.")
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
    Logs._log("Starting Names function ...")
    search_urls = []
    parse_name = lambda n: "".join(filter(lambda x: x.isalnum() or x == " ", n)).strip()
    Logs._log("Creating search URLs ...")
    for name in names:
        # Parse current name for URL query and add to search list - with no duplicate URLs
        query = parse_name(name)
        url = "https://www.celebritynetworth.com/dl/" + query.replace(" ", "-").lower() + "/"
        if url in search_urls: continue
        search_urls.append(url)
    Logs._log("Getting search results ...")
    # Collect the search result pages from the URLs
    results = bf.get_pages(search_urls)
    # Loop through the resulting search pages and store URL for profile in a list if valid
    profile_urls = []
    for i,page in enumerate(results):
        tag = "post_item anchored  search_result lead"
        lead = BeautifulSoup(page["html"],features=opt._PARSER,parse_only=SoupStrainer(attrs={"class":tag}))
        if lead:
            # There's a lead search result, check if the contents have our target's name
            current_name = parse_name(names[i])
            txt = lead.text.lower()
            if all([x in txt for x in current_name.lower().split()]):
                # It does - get the target's profile url and 
                Logs._log(f"FOUND: '{current_name}' matches with result.",True)
                profile_urls.append(lead.find("a")["href"])
            else:
                Logs._log(f"FAILED: '{current_name}' doesn't seem to match search result.\n",True)
        else:
            Logs._log(f"FAILED: Search for '{current_name}' returned no results.",True)
    # Get and parse the pages
    Logs._log("Getting matching profiles ...")
    profile_pages = bf.get_pages(profile_urls)
    profiles = [bf.parse_profile(page["html"]) for page in profile_pages]
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Names function finished.")
    return profiles

def scrape_top(category:Category=None,sort_by:str="",sort_ascending:bool=True):
    """
    Get the top 50 richest profiles from a category. If category is left at default (None), get the top 100 overall richest profiles in the world instead.\n
    :category: Enum from Category class to use. E.g. - category = Category.AUTHORS /OR/ category = None = Top 100 list\n
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.\n
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?\n
    :return: A list of Profile objects - optionally sorted.
    """
    Logs._log("Starting Top function ...")
    if category:
        # Check if there's a category and assign the appropriate URL
        if not isinstance(category,Category):
            raise Exception("Invalid Category Parameter")
        top_url = "https://www.celebritynetworth.com/list/top-50-" + category.value + "/"
    else:
        top_url = "https://www.celebritynetworth.com/list/top-100-richest-people-in-the-world/"
    Logs._log(f"Getting toplist page for {category.name if category else 'Top 100'} category ...")
    html = bf.get_pages([top_url])[0]["html"]
    Logs._log("Collecting profile URLs from list ...")
    # Get profiles from list inside page
    profiles = bf.get_profiles_from_list_in_page(html,"top_100_list")
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Top function finished.")
    return profiles

def scrape_random():
    """
    Uses the site's random feature to grab a random profile.\n
    :return: A single Profile object from a randomly chosen subject.
    """
    Logs._log("Starting Random function ...")
    url = "https://www.celebritynetworth.com/random/"
    html = bf.get_pages([url])[0]["html"]
    profile = bf.parse_profile(html)
    # Wrap up
    Logs._log("Profile compilation finished ...")
    Logs._log("Random function finished.")
    return profile