import datetime


def current_version_refbook(refbookobj, date=datetime.date.today()):
    """Текущая версия справочника на дату."""

    return refbookobj.versions.filter(
        start_date__lte=date
    ).order_by('-start_date').first()