from src.models import DealModel, NotificationModel


def start() -> str:
    return 'Folgende Benachrichtigungen sind aktiv:'


def help_msg() -> str:
    return 'Um den Bot zu starten, nutze das Kommando /start' \
           '\n\n<b>Suchbegriffe:</b>' \
           '\ncase-insensitive und führende/anhängende Leerzeichen werden entfernt.' \
           '\n-> "nutella&rewe,nutella&lidl" \nliefert die selben Ergebnisse wie \n"Nutella & REWE, Nutella & Lidl"' \
           '\n\n<b>Minimaler Preis:</b>' \
           '\nNur Benachrichtigungen für Deals mit höherer oder ohne Preisangabe' \
           '\n\n<b>Maximaler Preis:</b>' \
           '\nNur Benachrichtigungen für Deals mit niedrigerer oder ohne Preisangabe' \
           '\n\n<b>Reichweite:</b> ' \
           '\nAlle Deals -> Benachrichtigungen für alle Deals' \
           '\nNur heiße Deals -> Benachrichtigungen für Deals > 100°'


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
    return 'Suchbegriff: {query}\n' \
           'Minimaler Preis: {min_price}\n' \
           'Maximaler Preis: {max_price}\n' \
           'Reichweite: {range}'.format(
                query=notification.query,
                min_price=str(notification.min_price) + ' €' if notification.min_price else '-',
                max_price=str(notification.max_price) + ' €' if notification.max_price else '-',
                range=search_range
            )


def query_updated(notification: NotificationModel) -> str:
    return 'Suchbegriff aktualisiert\n\n{}'.format(notification_overview(notification))


def price_instructions(price_type: str) -> str:
    return 'Bitte gebe einen neuen {0}imal-Preis an. ' \
           '\n/remove um den {0}imal-Preis zu löschen' \
           '\n/cancel zum Abbrechen'.format(price_type)


def invalid_price(price_type: str) -> str:
    return 'Der eingegebene Preis ist ungültig!\n\n{}'.format(price_instructions(price_type))


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


def add_notification_inconclusive(text: str) -> str:
    return 'Möchtest Du eine Benachrichtigung für "{}" erstellen?'.format(text)


def notification_not_found() -> str:
    return 'Die Benachrichtigung wurde bereits gelöscht.'
