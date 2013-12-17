from django.conf import settings
import os.path

def _convert_file_to_url(filename, no_file_check = False):
    """In the normal case (no_file_check is False) reduce the filepath
    against the filesystem and content root.  If no_file_check is
    True, then don't do any of that and instead assume that the path
    passed is correct and in its ultimate form.

    """
    if no_file_check: # We already a priori know that the path is
                      # correct and in its final form.
        return filename
    relpath = os.path.relpath(filename, settings.SENDFILE_ROOT)

    url = [settings.SENDFILE_URL]

    while relpath:
        relpath, head = os.path.split(relpath)
        url.insert(1, head)

    return u'/'.join(url) # Note: xlates from os.path.sep to '/'
