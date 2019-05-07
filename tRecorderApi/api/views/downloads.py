from rest_framework import viewsets, status
from rest_framework.response import Response

from api.serializers import DownloadsSerializer
from api.models import Downloads

import os


class DownloadsViewSet(viewsets.ViewSet):
    serializer_class = DownloadsSerializer
    directory = "downloads"

    def _get_abs_virtual_root(self):
        return self._eventual_path(self.directory)

    def _inside_virtual_root(self, eventual_path):
        virtual_root = self._get_abs_virtual_root()
        return os.path.commonprefix([virtual_root, eventual_path]) == virtual_root

    def _eventual_path(self, path):
        return os.path.abspath(os.path.realpath(path))
        
    def get_names(self, directory):
        contents = os.listdir(directory)
        files = []
        for item in contents:
            candidate = os.path.join(directory, item)
            if os.path.isfile(candidate):
                download = Downloads()
                download.name = item
                download.url = os.path.join(self.directory, item)
                files.append(download)
        return files
        
    def _list_directory(self, request, directory):
        files = self.get_names(directory)
        serializer = DownloadsSerializer(
            instance=files, many=True)
        return Response(serializer.data)
        
    def list(self, request):
        virtual_root = self._get_abs_virtual_root()
    
        if not self._inside_virtual_root(virtual_root):
            # Someone is playing tricks with .. or %2e%2e or so
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return self._list_directory(request, virtual_root)
