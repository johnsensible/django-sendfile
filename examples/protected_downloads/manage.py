#!/usr/bin/env python

# from __future__ import absolute_import

#!/usr/bin/env python
import os
import sys

sys.path = [ os.path.join(os.path.dirname(__file__), '..', '..'), ] + sys.path

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
