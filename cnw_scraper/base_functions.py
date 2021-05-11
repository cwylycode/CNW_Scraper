# ---------- Base functionality for the program

import aiohttp
import asyncio
import os
from cnw_scraper.logs import Logs
from cnw_scraper.options import Options as opt
from cnw_scraper.profile import Profile
from bs4 import BeautifulSoup,SoupStrainer

# Prevents Windows-specific nonsense about "Event loop is closed" with asyncio loop policy
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def parse_profile(page_html):
    # Parse the HTML soup on the profile's page and return the data as a Profile object
    Logs._log("Parsing HTML ...",True)
    soup = BeautifulSoup(page_html,features=opt._PARSER,parse_only=SoupStrainer(attrs={"id":"single__main"}))
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
    if opt.include_description:
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
    Logs._log(f"Compiling profile of '{data['Name']}' ...",True)
    return Profile(data, desc)

async def fetch(url,session):
    try:
        # Get info and payload from a valid URL
        async with session.request(method="GET", url=url, timeout=opt._TIMEOUT) as response:
            html = await response.text()
            status = response.status
            data = {"status":status,"url":url,"html":html}
    except Exception as err:
        # Kill program if we have a connection error
        await asyncio.sleep(0.5)
        raise err
    Logs._log(f"Fetched page: '{data['status']}' - {data['url']}",True)
    return data

async def client(urls):
    # Asynchronously get the requested pages and return list of multiple page HTML responses
    Logs._log("Establishing connection ...",True)
    ua = opt.custom_user_agent if opt.custom_user_agent else opt._DEFAULT_UA
    async with aiohttp.ClientSession(headers={"user-agent":ua}) as session:
        tasks = [fetch(url,session) for url in urls]
        page_list = await asyncio.gather(*tasks)
    await asyncio.sleep(0.5) # Graceful shutdown of client connections is needed
    Logs._log("Collected pages from URLs ...",True)
    return page_list

def get_pages(urls):
    # Initialize an async client run to connect to site and collect the HTML data from the supplied URLs
    Logs._log(f"Getting ({len(urls)}) page(s) ...",True)
    pages = asyncio.run(client(urls))
    Logs._log("Compiling page list ...",True)
    return list(pages)

def get_profiles_from_list_in_page(base_page,target_id):
    # Run page through soup and get each listed profile URL inside it
    profile_list = BeautifulSoup(base_page,features=opt._PARSER,parse_only=SoupStrainer(attrs={"id":target_id}))
    if not profile_list:
        Logs._log("No Profiles found!")
        return []
    profile_urls = [a["href"] for a in profile_list.select("a")]
    # Get profiles from URLs
    profile_pages = get_pages(profile_urls)
    profiles = [parse_profile(page["html"]) for page in profile_pages]
    return profiles

def sort_profiles(profiles,sort_by,sort_ascending):
    if sort_by and sort_by in ["name","worth"]:
        # Key to sort by either profile name or net worth
        k = lambda x: x.stats["Name"] if sort_by == "name" else int(x.stats["Net Worth"])
        Logs._log(f"Sorting Profiles by {sort_by.capitalize()} ({'Ascending' if sort_ascending else 'Descending'}) ...")
        profiles = sorted(profiles,key=k,reverse=not sort_ascending)
    return profiles