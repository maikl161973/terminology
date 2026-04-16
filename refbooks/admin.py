from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin)
from django.contrib.auth.models import User, Group

from .helpers import current_version_refbook
from .models import RefBook, Version, Element, Role, GroupRole

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
        version = current_version_refbook(obj)
        return version.version if version else '-'

    def current_version_start_date(self, obj):
        version = current_version_refbook(obj)
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


class RoleAdmin(admin.ModelAdmin):
    """Админка для справочника ролей"""

    list_display = ('id', 'code', 'name')
    fields = ('code', 'name')
    search_fields = ('name', 'code')
    verbose_name = verbose_name_plural = 'Справочник ролей'


class GroupRoleInline(admin.TabularInline):
    model = GroupRole
    extra = 1
    verbose_name = verbose_name_plural = 'Роль группы'
    autocomplete_fields = ('role',)
    max_num = 1


class GroupAdmin(BaseGroupAdmin):
    inlines = [GroupRoleInline]


class GroupRoleAdmin(admin.ModelAdmin):
    list_display = ('group', 'role')
    list_filter = ('role__name',)
    autocomplete_fields = ('group', 'role')
    search_fields = ('group__name', 'role__name')
    verbose_name = verbose_name_plural = 'Роли групп'


admin.site.register(RefBook, RefBookAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(GroupRole, GroupRoleAdmin)

# Group с inline
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

# Восстанавливаем стандартный UserAdmin
admin.site.unregister(User)
admin.site.register(User, BaseUserAdmin)
