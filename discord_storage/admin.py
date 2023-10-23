from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import ChunkedFile, File

admin.site.register(File)


class ChunkedFileAdmin(ImportExportModelAdmin):
    fields = (
        "uuid",
        "file_name",
        "file_size",
        "chunked_file_count",
        "created_at",
    )
    readonly_fields = (
        "uuid",
        "file_name",
        "file_size",
        "chunked_file_count",
        "created_at",
    )

    def chunked_file_count(self, obj):
        return len(obj.file_urls.split(","))


admin.site.register(ChunkedFile, ChunkedFileAdmin)
