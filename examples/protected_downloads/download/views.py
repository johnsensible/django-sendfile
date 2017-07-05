from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext

from sendfile.core import sendfile

from download.models import Download


def download(request, download_id):
    download = get_object_or_404(Download, pk=download_id)
    if download.is_public:
        return sendfile(request, download.file.path)
    return _auth_download(request, download)


@login_required
def _auth_download(request, download):
    if not download.is_user_allowed(request.user):
        return HttpResponseForbidden('Sorry, you cannot access this file')
    return sendfile(request, download.file.path)


def download_list(request):
    downloads = Download.objects.all()
    if request.user.is_authenticated():
        downloads = downloads.filter(Q(is_public=True) | Q(users=request.user))
    else:
        downloads = downloads.filter(is_public=True)
    return render_to_response('download/download_list.html',
                              {'download_list': downloads},
                              context_instance=RequestContext(request))
