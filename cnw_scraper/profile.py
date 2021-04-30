class _Profile:
    """
    Contains information from a subject's net worth page (print me for a pretty display of my contents). This object isn't created directly, but rather is made through the api functions.\n
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