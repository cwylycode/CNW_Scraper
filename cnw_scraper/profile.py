class Profile:
    """
    An object that ontains information from a subject's net worth page (print me for a pretty display of my contents). This object isn't created directly, but rather is made through the scrape functions.

    Note: Certain stats for certain profiles might not exist, as the profile simply doesn't have them on the site. A profile will always have at least a name.

    :stats: Dictionary containing name, net worth, salary, gender, nationality, etc. - Net Worth gets printed out as a dollar amount, but is actually stored as a real number string.

    :description: String containing the bio of the subject - optional.

    :fields: Static class attribute. Helper list showing all known stats that make up any profile on the site. Useful for writing these as columns to CSV so you don't have to add them yourself through trial and error. These might change in the future as the site may or may not update the profiles with more stats.
    """

    fields = [
        "Name",
        "Net Worth",
        "Salary",
        "Date of Birth",
        "Gender",
        "Height",
        "Profession",
        "Nationality",
        "Last Updated",
    ]

    def __init__(self, stats:dict, description:str):
        self.stats = stats
        self.description = description

    def __str__(self):
        stats = dict(self.stats)
        stats["Net Worth"] = f"${int(stats['Net Worth']):,}"
        x = "".join([f"{key}: {value}\n" for key,value in stats.items()])
        y = self.description[:199]+" ..." if len(self.description) > 200 else self.description
        return x+"Description: "+y