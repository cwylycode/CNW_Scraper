from aiohttp import ClientTimeout

class Options: 
    """
    Change certain options here.

    :custom_user_agent: Send a different user-agent string to the site when connecting, instead of the default one.
    
    :include_description: True by default. Change to false if you don't want your collected profiles to include the description portion (which can be lengthy and arguably needless for data processing).
    """
    custom_user_agent = ""
    include_description = True
    _DEFAULT_UA = "Totally Not A Bot"
    _PARSER = "html.parser"
    _TIMEOUT = ClientTimeout(total=15,connect=10)