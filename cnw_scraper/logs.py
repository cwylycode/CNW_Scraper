import logging
import inspect
import os

class Logs:
    """
    Handles logging of what this program is doing. It will write logs to either a file or console, or both. Use write_to_file function to write logs to a file at a specified path. The log file, if present, gets overwritten each run, so if you want to save a log file, simply rename the actual file to something else.
    
    Note: All of the following boolean values are False by default.
    
    :print_to_console: Use print function to print logs to console?
    
    :verbose: Some parts of the program use extensive logging for every detail. Enable the extra logging?
    """
    print_to_console = False
    verbose = False
    _logger = None

    @classmethod
    def write_to_file(cls,file_path:str="",include_datetime:bool=True):
        """
        Initialize logging to a .log file using an established directory. Subsequent calls do nothing, only the first call does anything. If the file_path argument is left out, the default arg is used. The default path is the directory level that calls this function and the name is collected from __main__ with modifications. E.g. - 'my_script.py' -> 'my_script-cnw.log'
        
        Note: File is created if it isn't there, and if it is, it will be overwritten. Also, actual file writing only occurs upon program exit.
        
        :file_path: Provide an optional valid directory path (relative to where this function was called from or absolute) and name for the file (name will end with a '.log' extension). E.g. - './my_project/logs/my_cnw_logs' -> 'my_cnw_logs.log' file in logs directory.
        
        :include_datetime: Bool for whether or not to include a formatted date/time marker for each log entry that gets written out to the file.
        
        :return: None
        """
        if cls._logger: return
        path = os.path.split([i.filename for i in inspect.stack()][-1])
        log_file = file_path if file_path else "".join([path[0],"/",path[1].replace(".py",""),"-cnw"])
        frmt = "%(asctime)s - LOG: %(message)s" if include_datetime else "LOG: %(message)s"
        logging.basicConfig(filename=log_file+".log",filemode="w",format=frmt,datefmt="%Y-%m-%d %X",level="INFO")
        cls._logger = logging.getLogger()

    @classmethod
    def _log(cls,txt,is_verbose=False):
        # Used for printing/writing status updates and logging for the application
        if not cls.verbose and is_verbose: return
        if cls._logger: cls._logger.info(txt)
        if cls.print_to_console: print("CNW - "+txt)