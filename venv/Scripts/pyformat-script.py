#!F:\Parser\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pyformat==0.7','console_scripts','pyformat'
__requires__ = 'pyformat==0.7'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pyformat==0.7', 'console_scripts', 'pyformat')()
    )
