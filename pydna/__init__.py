#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os               as _os
import sys              as _sys
import subprocess       as _subprocess
import logging          as _logging
import logging.handlers as _handlers
import appdirs          as _appdirs
import configparser     as _configparser
import prettytable      as _prettytable
import importlib        as _importlib
'''
# pydna

The pydna package.

:copyright: Copyright 2013 - 2016 by Björn Johansson. All rights reserved.
:license:   This code is part of the pydna distribution and governed by its
            license.  Please see the LICENSE.txt file that should have been included
            as part of this package.

'''

__author__       = "Björn Johansson"
__copyright__    = "Copyright 2013 - 2015 Björn Johansson"
__credits__      = ["Björn Johansson", "Mark Budde"]
__license__      = "BSD"
__maintainer__   = "Björn Johansson"
__email__        = "bjorn_johansson@bio.uminho.pt"
__status__       = "Development" # "Production" #"Prototype"




from pydna import _version
__version__      = _version.get_versions()['version'][:5]
__long_version__ = _version.get_versions()['version']
del _version
_sys.modules.pop("pydna._version", None)


'''
Pydna can cache results from the following functions or methods:

    Genbank_nucleotide
    Anneal
    Assembly
    download_text
    Dseqrecord_synced
    Genbank_nucleotide

These can be added separated by a comma to the 
pydna_cached_funcs environment variable.

'''
# create config directory
_os.environ["pydna_config_dir"] = _os.getenv("pydna_config_dir", _appdirs.user_config_dir("pydna"))
try:
    _os.makedirs( _os.environ["pydna_config_dir"] )
except OSError:
    if not _os.path.isdir( _os.environ["pydna_config_dir"] ):
        raise

# set path for the pydna.ini file
_ini_path = _os.path.join( _os.environ["pydna_config_dir"], "pydna.ini" )

# initiate a config parser instance
_parser = _configparser.ConfigParser()

# if a pydna.ini exists, it is read
if _os.path.exists(_ini_path):
    _parser.read(_ini_path)
else: # otherwise it is created with default settings
    with open(_ini_path, 'w', encoding="utf-8") as f:    # TODO needs encoding?
        _parser["main"] = { 'loglevel': str(_logging.WARNING),
                            'email'   : "someone@example.com",
                            'data_dir': _appdirs.user_data_dir("pydna"),
                            'log_dir' : _appdirs.user_log_dir("pydna"),
                            'cached_funcs':'Genbank_nucleotide',
                            'ape'     : 'put/path/to/ape/here',
                            'primers' : 'put/path/to/primers/here',
                            'enzymes' : 'put/path/to/enzymes/here'}
        _parser.write(f)

# pydna related environmental variables are set from pydna.ini if they are not set already
_mainsection = _parser["main"]
_os.environ["pydna_loglevel"] = _os.getenv("pydna_loglevel", _mainsection.get("loglevel",str(_logging.WARNING)))
_os.environ["pydna_email"]    = _os.getenv("pydna_email",    _mainsection.get("email","someone@example.com"))
_os.environ["pydna_data_dir"] = _os.getenv("pydna_data_dir", _mainsection.get("data_dir",_appdirs.user_data_dir("pydna")))
_os.environ["pydna_log_dir"]  = _os.getenv("pydna_log_dir",  _mainsection.get("log_dir",_appdirs.user_log_dir("pydna")))
_os.environ["pydna_cached_funcs"] = _os.getenv("cached_funcs", _mainsection.get("cached_funcs", 'none'))
_os.environ["pydna_ape"]      = _os.getenv("pydna_ape",      _mainsection.get("ape",'put/path/to/ape/here'))
_os.environ["pydna_primers"]  = _os.getenv("pydna_primers",  _mainsection.get("primers", 'put/path/to/primers/here'))
_os.environ["pydna_enzymes"]  = _os.getenv("pydna_enzymes",  _mainsection.get("enzymes", 'put/path/to/enzymes/here'))


# create log directory if not present
_os.makedirs( _os.environ["pydna_log_dir"], exist_ok=True)                     #### changes to file system ####
_logmsg = "Log directory {}".format(_os.environ["pydna_log_dir"])

# create logger
_logger = _logging.getLogger("pydna")
_logger.setLevel( int(_os.environ["pydna_loglevel"]) )
_hdlr = _handlers.RotatingFileHandler(_os.path.join( _os.environ["pydna_log_dir"] , 'pydna.log'), mode='a', maxBytes=10*1024*1024, backupCount=10, encoding='utf-8')
_formatter = _logging.Formatter('%(asctime)s %(levelname)s %(funcName)s %(message)s')
_hdlr.setFormatter(_formatter)
_logger.addHandler(_hdlr)
_logger.info(_logmsg)
_logger.info('Assigning environmental variable pydna_data_dir = %s', _os.environ["pydna_data_dir"] )

# create cache directory if not present

_os.makedirs( _os.environ["pydna_data_dir"], exist_ok=True)                              #### changes to file system ####
_logger.info("Data directory %s", _os.environ["pydna_data_dir"] )

# find out if optional dependecies for gel module are in place
_missing_modules_for_gel = []

for _optm in ["scipy","numpy", "matplotlib", "mpldatacursor", "pint"]:
    _missing_modules_for_gel.extend( [_optm] if not _importlib.util.find_spec(_optm) else [])

if _missing_modules_for_gel:
    _logger.warning("gel simulation will NOT be available. Missing modules: %s",
                     ", ".join(_missing_modules_for_gel))
else:
    _logger.info("gel simulation will be available.")

class _PydnaWarning(Warning):
    """Pydna warning.

    Pydna uses this warning (or subclasses of it), to make it easy to
    silence all warning messages:

    >>> import warnings
    >>> from pydna import _PydnaWarning
    >>> warnings.simplefilter('ignore', _PydnaWarning)

    Consult the warnings module documentation for more details.
    """
    pass

class _PydnaDeprecationWarning(_PydnaWarning):
    """pydna deprecation warning.

    Pydna uses this warning instead of the built in DeprecationWarning
    since those are ignored by default since Python 2.7.

    To silence all our deprecation warning messages, use:

    >>> import warnings
    >>> from pydna import _PydnaDeprecationWarning
    >>> warnings.simplefilter('ignore', _PydnaDeprecationWarning)

    Code marked as deprecated will be removed in a future version
    of Pydna. This can be discussed in the Pydna google group:
    https://groups.google.com/forum/#!forum/pydna    
    
    """
    pass

def open_current_folder():
    return _open_folder( _os.getcwd() )
    
def open_cache_folder():
    return _open_folder( _os.environ["pydna_data_dir"] )

def open_config_folder():
    return _open_folder( _os.environ["pydna_config_dir"] )

def open_log_folder():
    return _open_folder( _os.environ["pydna_log_dir"] )

def _open_folder(pth):
    if _sys.platform=='win32':
        _subprocess.run(['start', pth], shell=True)
    elif _sys.platform=='darwin':
        _subprocess.run(['open', pth])
    else:
        try:
            _subprocess.run(['xdg-open', pth])
        except OSError:
            return "no cache to open."

def get_env():
    from pydna._pretty import pretty_str  as _pretty_str
    _table = _prettytable.PrettyTable(["Variable", "Value"])
    _table.set_style(_prettytable.DEFAULT)
    _table.align["Variable"] = "l" # Left align
    _table.align["Value"] = "l" # Left align
    _table.padding_width = 1 # One space between column edges and contents
    for k,v in sorted(_os.environ.items()):
        if k.startswith("pydna"):
            _table.add_row([k,v])
    return _pretty_str(_table)

def logo():
    from pydna._pretty import pretty_str  as _pretty_str
    return _pretty_str("                 _             \n"       
                       "                | |            \n"            
                       " ____  _   _  __| |___   __ ___\n"
                       "|  _ \| | | |/ _  |  _ \(____ |\n"
                       "| |_| | |_| ( (_| | | | / ___ |\n"
                       "|  __/ \__  |\____|_| |_\_____|\n"
                       "|_|   (____/                   \n")

if __name__=="__main__":
    import os as _os
    cached = _os.getenv("pydna_cached_funcs", "")
    _os.environ["pydna_cached_funcs"]=""
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
    _os.environ["pydna_cached_funcs"]=cached