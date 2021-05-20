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
    _TIMEOUT = ClientTimeout(total=300)

    @classmethod
    def set_http_timeout(cls,total:float=300,connect:float=None,socket_read:float=None,socket_connect:float=None):
        """
        Change the timeout values for the aiohttp session connections. All values map directly to a ClientTimeout object and are float numbers in seconds. By default, session connections will last for 5 minutes (total=300 seconds). Use this function if you need more time to complete a scraping task (e.g. for using scrape_names to get an enormous number of profiles). Refer to the aiohttp ClientTimeout docs for more information.

        :total: How long a connection will last at the latest.

        :connect: How long to wait for a connection from the pool of connections.

        :socket_read: How long to wait in between data being read from a peer.

        :socket_connect: How long to wait for a connection to a peer.

        :return: None.
        """
        cls._TIMEOUT = ClientTimeout(
        total=total,
        connect=connect,
        sock_read=socket_read,
        sock_connect=socket_connect)