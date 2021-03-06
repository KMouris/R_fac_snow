from config_input import logging  # CHANGE: calls all folders input file "config_input", which contains all variables

#                                   and imports all needed modules

# define name and location of logfile
log_file = "./logfile.log"

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode="a",
                    format="%(asctime)-15s %(levelname)-8s %(message)s")
logger = logging.getLogger("logger")

# Configure streamhandler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s"))

logger.addHandler(stream_handler)


def wrapper(pre, post):
    """
    Simple wrap function, Wrapper decorator @ is to be placed right on top of function to be wrapped
    :param pre: Function called before the function that is being wrapped
    :param post: Function called after the function that is being wrapped
    """

    def decorator(function):
        def inner(*args, **kwargs):
            # function that is called before executing wrapped function
            pre(function)
            # execute wrapped function
            result = function(*args, **kwargs)
            # function that is called after executing wrapped function
            post(function)
            return result

        return inner

    return decorator


def entering(function):
    """
    Function that logs when a wrapped function is called / entered
    :param function:
    """
    logger.debug("Entered %s", function.__name__)


def exiting(function):
    """
    Function that logs when a wrapped function is exited
    :param function:
    """
    logger.debug("Exited  %s", function.__name__)
