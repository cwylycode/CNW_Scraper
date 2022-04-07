from enum import Enum

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