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
           '\nGültige Zeichen: (Buchstaben, Zahlen - , + & .)' \
           '\nFür ein Multi-Matching nutze & (z.B.: zelda&switch)' \
           '\nUm ein Wort auszuschließen nutze ! & (z.B.: PS5 & !lokal)' \
           '\n/cancel zum Abbrechen'


def invalid_query() -> str:
    return f'Der Suchbegriff ist ungültig!\n\n{query_instructions()}'


def notification_added(notification: NotificationModel) -> str:
    return f'Benachrichtigung angelegt\n\n{notification_overview(notification)}'


def notification_overview(notification: NotificationModel) -> str:
    search_range = 'Nur heiße Deals' if notification.search_only_hot else 'Alle Deals'
    return (
        f'Suchbegriff: {notification.query}\n'
        f'Minimaler Preis: {str(notification.min_price) + " €" if notification.min_price else "-"}\n'
        f'Maximaler Preis: {str(notification.max_price) + " €" if notification.max_price else "-"}\n'
        f'Reichweite: {search_range}\n'
        f'Mindstar durchsuchen: {"Ja" if notification.search_mindstar else "Nein"}'
    )


def query_updated(notification: NotificationModel) -> str:
    return f'Suchbegriff aktualisiert\n\n{notification_overview(notification)}'


def price_instructions(price_type: str) -> str:
    return (
        f'Bitte gebe einen neuen {price_type}imal-Preis an.\n'
        f'/remove um den {price_type}imal-Preis zu löschen\n'
        '/cancel zum Abbrechen'
    )


def invalid_price(price_type: str) -> str:
    return f'Der eingegebene Preis ist ungültig!\n\n{price_instructions(price_type)}'


def notification_deleted(notification: NotificationModel) -> str:
    return f'Benachrichtigung "{notification.query}" gelöscht'


def deal_msg(deal: DealModel, notification: NotificationModel) -> str:
    message = f'Neuer Deal für "{notification.query}":\n<a href="{deal.link}">{deal.title}</a>'

    if deal.price:
        message += f'\n Preis: {deal.price:.2f} €'

    return message


def add_notification_inconclusive(text: str) -> str:
    return f'Möchtest Du eine Benachrichtigung für "{text}" erstellen?'


def notification_not_found() -> str:
    return 'Die Benachrichtigung wurde bereits gelöscht.'
