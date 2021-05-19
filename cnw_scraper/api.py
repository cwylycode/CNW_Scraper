# ---------- Main API for the user

import cnw_scraper.base_functions as bf
from cnw_scraper.categories import Category
from cnw_scraper.locations import Location
from cnw_scraper.logs import Logs
from cnw_scraper.options import Options as opt
from bs4 import BeautifulSoup,SoupStrainer

def scrape_category(category:Category,starting_page:int=1,ending_page:int=0,sort_by:str="",sort_ascending:bool=True):
    """
    Get the profiles from a category within a page range. Pages are scraped from the very start of the starting page, all the way to the very last profile on the ending page. By default, get only the profiles from the first page of the category. All categories start on page 1.
    
    Note: Some categories have hundreds of pages and thousands of profiles and may take a considerable amount of time to collect them all (relative to the other scrape functions).
    
    Tip: Because the website offers no method of getting the total number of pages in a category (without visiting the page to see if it is valid - or through hacking), it is up to the user to determine what the starting and ending pages should be. This is done to speed up page collection for async HTTP requests. It's best to test how many pages exist first before collecting them. Out-of-range pages will return a 404 and will be safely filtered out upon profile parsing. Don't set the ending page too high otherwise the requested pages will be mostly 404 junk - and that wastes electricity and bandwidth. Think about the environment.
    
    :category: Enum from Category class to use. E.g. - category = Category.AUTHORS
    
    :starting_page: The page to start scraping (>0). If less than 1, it will be set to 1.
    
    :ending_page: The last page to scrape (>=starting_page). Inclusive. If less than starting_page, it will be set to starting_page.
    
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.
    
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?
    
    :return: A list of Profile objects - optionally sorted.
    """
    Logs._log("Starting Category function ...")
    if starting_page < 1:
        starting_page = 1
    if not isinstance(category,Category):
        raise Exception("Invalid Category Parameter.")
    if starting_page > ending_page:
        ending_page = starting_page
    base_url = "https://www.celebritynetworth.com/category/" + category.value + "/page/"
    # Get category pages containing profiles from start to end, filtering out 404s.
    Logs._log(f"Getting pages from {category.name} category ...")
    cat_urls = [base_url+str(i)+"/" for i in range(starting_page,ending_page+1)]
    Logs._log(f"Getting {len(cat_urls)} page(s) ...")
    cat_pages = list(filter(lambda x: not (x["status"]>=400), bf.get_pages(cat_urls)))
    Logs._log(f"Collected {len(cat_pages)} valid page(s) ...")
    # Get profiles
    profiles = []
    if cat_pages:
        # Get all profile links in the pages
        profile_urls = []
        for page in cat_pages:
            profile_urls.extend(bf.get_profile_links_in_page(page["html"],"post_listing"))
        # Get profiles from pages and parse them
        Logs._log(f"Getting {len(profile_urls)} profile(s) from pages ...")
        profile_pages = bf.get_pages(profile_urls)
        Logs._log("Parsing pages of profiles ...")
        profiles = [bf.parse_profile(page["html"]) for page in profile_pages]
    else:
        # The result of nothing but invalid pages
        Logs._log("No Profiles found!")
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Category function finished.")
    return profiles

def scrape_map(location:Location,sort_by:str="",sort_ascending:bool=True):
    """
    Get the top 100 profiles from a map location on the site.
    
    :location: Enum from Location class to use. E.g. - location = Location.USA
    
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.
    
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?
    
    :return: A list of Profile objects - optionally sorted.
    """
    Logs._log("Starting Map function ...")
    if not isinstance(location,Location):
        raise Exception("Invalid Location Parameter")
    Logs._log(f"Getting map page for {location.name} ...")
    map_url = "https://www.celebritynetworth.com/map/" + location.value + "/"
    html = bf.get_pages([map_url])[0]["html"]
    Logs._log("Collecting profile URLs from map ...")
    # Get profile links from list inside page and parse the profiles
    profile_urls = bf.get_profile_links_in_page(html,"cnwMaps_mainProfileList")
    profile_pages = bf.get_pages(profile_urls)
    profiles = [bf.parse_profile(page["html"]) for page in profile_pages]
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Map function finished.")
    return profiles

def scrape_names(names:list,sort_by:str="",sort_ascending:bool=True):
    """
    Use the site's search feature to check for each name provided and collect profile data on the subject if the name matches the query. If a name isn't found/doesn't match, no profile for it will be returned.
    
    Tip: Be sure to not use prefixes (Dr./Mr./Mrs./etc.) - suffixes are usually fine, and use only one space between words - the search engine on the site can be picky. Usually the first/last name is enough to get the right profile. Also, duplicate names are discarded - only one unique profile will be returned per name.
    
    :names: An iterable of strings, with each being the real name (and/or 'stage name') of a person/thing (alphanumeric/spaces only, symbols get stripped). E.g. - ['Elon Musk', 'Apple', 'OPRAH', 'DEADMAU5', 'bill gates', 'Dwayne "The Rock" Johnson', 'The Undertaker']
    
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.
    
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?
    
    :return: A list of Profile objects - optionally sorted.
    """
    Logs._log("Starting Names function ...")
    search_urls = []
    parse_name = lambda n: "".join(filter(lambda x: x.isalnum() or x == " " or x == "-", n)).strip()
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
    # Loop through the resulting search pages and store the profile's URL in a list if valid
    profile_urls = []
    tag = "post_item anchored  search_result lead"
    for i,page in enumerate(results):
        lead = BeautifulSoup(page["html"],features=opt._PARSER,parse_only=SoupStrainer(attrs={"class":tag}))
        current_name = parse_name(names[i])
        if lead.text:
            # There's a lead search result, check if the contents have our target's name
            txt = lead.text.lower()
            if all([x in txt for x in current_name.lower().split()]):
                # It does - get the target's profile url
                Logs._log(f"FOUND: '{current_name}' matches with result.",True)
                profile_urls.append(lead.find("a")["href"])
            else:
                Logs._log(f"FAILED: '{current_name}' doesn't seem to match search result.",True)
        else:
            Logs._log(f"FAILED: Search for '{current_name}' returned no results.",True)
    # Get and parse the profiles
    Logs._log("Getting matching profiles ...")
    profile_pages = bf.get_pages(profile_urls)
    profiles = [bf.parse_profile(page["html"]) for page in profile_pages]
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Names function finished.")
    return profiles

def scrape_random():
    """
    Uses the site's random feature to grab a random profile.
    
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

def scrape_top(category:Category=None,sort_by:str="",sort_ascending:bool=True):
    """
    Get the top 50 richest profiles from a category. If category is left at default (None), get the top 100 overall richest profiles in the world instead.
    
    :category: Enum from Category class to use. E.g. - category = Category.AUTHORS /OR/ category = None = Top 100 list
    
    :sort_by: Sort the list of profiles by either 'name' or 'worth' - default (empty string), or invalid, means no sorting is applied.
    
    :sort_ascending: Should the sorted profiles be returned in ascending or descending form?
    
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
    profile_urls = bf.get_profile_links_in_page(html,"top_100_list")
    profile_pages = bf.get_pages(profile_urls)
    profiles = [bf.parse_profile(page["html"]) for page in profile_pages]
    # Wrap up
    Logs._log("Profiles compilation finished ...")
    profiles = bf.sort_profiles(profiles,sort_by,sort_ascending)
    Logs._log("Top function finished.")
    return profiles