from src.models import NotificationModel, DealModel


def start() -> str:
    return 'Folgende Benachrichtigungen sind aktiv:'


def query_instructions() -> str:
    return 'Bitte gebe eine Liste aus kommaseparierten Suchbegriffen ein.' \
           '\nGültige Zeichen: (Buchstaben, Zahlen - , + &)' \
           '\nFür ein Multi-Matching nutze & (z.B.: zelda&switch)' \
           '\n/cancel zum Abbrechen'


def invalid_query() -> str:
    return 'Der Suchbegriff ist ungültig!\n\n{}'.format(query_instructions())


def notification_added(notification: NotificationModel) -> str:
    return 'Benachrichtigung angelegt\n\n{}'.format(notification_overview(notification))


def notification_overview(notification: NotificationModel) -> str:
    search_range = 'Nur heiße Deals' if notification.search_only_hot else 'Alle Deals'
    return 'Suchbegriff: {query}\nMaximaler Preis: {max_price}\nReichweite: {range}'.format(
        query=notification.query,
        max_price=str(notification.max_price) + ' €' if notification.max_price else '-',
        range=search_range
    )


def query_updated(notification: NotificationModel) -> str:
    return 'Suchbegriff aktualisiert\n\n{}'.format(notification_overview(notification))


def price_instructions() -> str:
    return 'Bitte gebe einen neuen Maximal-Preis an. ' \
           '\n/remove um den Maximal-Preis zu löschen' \
           '\n/cancel zum Abbrechen'


def invalid_price() -> str:
    return 'Der eingegebene Preis ist ungültig!\n\n{}'.format(price_instructions())


def notification_deleted(notification: NotificationModel) -> str:
    return 'Benachrichtigung "{}" gelöscht'.format(notification.query)


def deal_msg(deal: DealModel, notification: NotificationModel) -> str:
    message = 'Neuer Deal für "{query}":\n<a href="{link}">{title}</a>'.format(
        query=notification.query,
        link=deal.link,
        title=deal.title
    )

    if deal.price:
        message += '\n Preis: {:.2f} €'.format(deal.price)

    return message
