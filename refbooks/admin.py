from django.contrib import admin

from .models import RefBook, Version, Element

admin.site.site_header = (
    'Администрирование приложения "Справочники терминологий"')


class VersionInline(admin.TabularInline):
    model = Version
    extra = 1
    fields = ('version', 'start_date')
    verbose_name = verbose_name_plural = 'Версии справочника'
    show_change_link = True


class RefBookAdmin(admin.ModelAdmin):
    list_display = list_display_links = (
        'id', 'code', 'name', 'current_version', 'current_version_start_date')
    fields = ('code', 'name', 'description')
    inlines = [VersionInline]

    def current_version(self, obj):
        version = obj.current_version()
        return version.version if version else '-'

    def current_version_start_date(self, obj):
        version = obj.current_version()
        return version.start_date if version else '-'

    current_version.short_description = 'Текущая версия'
    current_version_start_date.short_description = 'Дата начала действия версии'


class ElementInline(admin.TabularInline):
    model = Element
    extra = 1
    fields = ('code', 'value')
    verbose_name = verbose_name_plural = 'Элементы справочникa'


class VersionAdmin(admin.ModelAdmin):
    list_display = list_display_links = (
        'ref_book_code', 'ref_book_name', 'version', 'start_date')
    fields = ('ref_book', 'version', 'start_date')
    inlines = [ElementInline]

    def ref_book_code(self, obj):
        return obj.ref_book.code

    def ref_book_name(self, obj):
        return obj.ref_book.name

    ref_book_code.short_description = 'Код справочника'
    ref_book_name.short_description = 'Наименование справочника'


class ElementAdmin(admin.ModelAdmin):
    list_display = ('version', 'code', 'value')
    fields = ('version', 'code', 'value')
    raw_id_fields = ('version',)


admin.site.register(RefBook, RefBookAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Element, ElementAdmin)
