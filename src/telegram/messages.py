import textwrap

from src.models import DealModel, NotificationModel, UserModel
from src.telegram.constants import Commands


def start(user: UserModel) -> str:
    return f'{settings(user)}\n' \
           f'Nutze /{Commands.SETTINGS} zum anpassen\n\n' \
           f'Folgende Suchbegriffe sind aktiv:'


def help_msg() -> str:
    return textwrap.dedent(
        '''
        <b><u>Suchbegriffe:</u></b>
        <b>-Groß- und Kleinschreibung werden nicht berücksichtigt
        - Leerzeichen werden entfernt
        - Standardmäßig wird ein Multi-Match verwendet</b>
        "<i>nutella&rewe</i>", "<i>Nutella & REWE</i>", und "<i>Nutella Rewe</i>" werden als "<i>nutella & rewe</i>" gespeichert.

        <b>Für mehrere Suchbegriffe benutze ein ",":</b>
        "<i>Nutella, Ovomaltine</i>" sucht nach Nutella oder Ovomaltine.

        <b>Um nach einem Leerzeichen zu suchen, benutze ein "+":</b>
        "<i>3060+TI</i>" liefert alle Deals mit "3060 TI" im Titel
        ("<i>3060 TI</i>" würde auch bei einem Deal mit dem Titel "RTX 3060 und Gra<b>ti</b>s Mauspad" anschlagen).

        <b>Um nach einem bestimmten Shop zu suchen, nutze eckige Klammern:</b>
        "<i>[Saturn], [Media+Markt]</i>" liefert alle Deals bei denen Saturn oder Media Markt als Händler hinterlegt ist.

        <b><u>Minimaler Preis:</u></b>
        Nur Benachrichtigungen für Deals mit höherer oder ohne Preisangabe

        <b><u>Maximaler Preis:</u></b>
        Nur Benachrichtigungen für Deals mit niedrigerer oder ohne Preisangabe

        <b><u>Reichweite:</u></b>
        Alle Deals -> Benachrichtigungen für alle Deals
        Nur heiße Deals -> Benachrichtigungen für Deals mit mehr als 100°

        <b><u>Unterstützte Websites:</u></b>
        - mydealz.de
        - preisjaeger.at
        - MindStar (mindfactory.de/Highlights/MindStar)
        mit /settings kann angepasst werden, welche Websites durchsucht werden sollen.
        '''
    )


def query_instructions() -> str:
    return 'Bitte gebe eine Liste aus kommaseparierten Suchbegriffen ein.' \
           '\nGültige Zeichen: (Buchstaben, Zahlen - , + & ! [ ])' \
           '\n/help für mehr Details' \
           '\n/cancel zum abbrechen'


def invalid_query() -> str:
    return f'Der Suchbegriff ist ungültig!\n\n{query_instructions()}'


def notification_added(notification: NotificationModel) -> str:
    return f'Suchbegriff angelegt\n\n{notification_overview(notification)}'


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
    return f'Suchbegriff "{notification.query}" gelöscht'


def deal_msg(deal: DealModel, notification: NotificationModel) -> str:
    message = f'Neuer Deal für "{notification.query}":\n<a href="{deal.link}">{deal.title}</a>'

    if deal.price.amount:
        message += f'\n Preis: {deal.price.amount:.2f} {deal.price.currency}'

    return message


def add_notification_inconclusive(text: str) -> str:
    return f'Möchtest Du eine Suchbegriff für "{text}" erstellen?'


def notification_not_found() -> str:
    return 'Der Suchbegriff wurde bereits gelöscht.'


def settings(user: UserModel) -> str:  # pylint: disable =unused-argument
    pages = []
    if user.search_mydealz:
        pages.append('mydealz.de')
    if user.search_mindstar:
        pages.append('MindStar (mindfactory.de/Highlights/MindStar)')
    if user.search_preisjaeger:
        pages.append('preisjaeger.at')

    message = 'Folgende Websites werden durchsucht:'
    for page in pages:
        message += f'\n + {page}'

    return message
