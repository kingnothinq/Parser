#!F:\Parser\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'unify==0.5','console_scripts','unify'
__requires__ = 'unify==0.5'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('unify==0.5', 'console_scripts', 'unify')()
    )
