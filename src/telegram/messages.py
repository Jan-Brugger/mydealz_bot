from __future__ import annotations

import html
import textwrap
from typing import TYPE_CHECKING

from src.telegram.enums import BotCommand

if TYPE_CHECKING:
    from src.models import DealModel, NotificationModel, UserModel


class Messages:
    @staticmethod
    def start(user: UserModel) -> str:
        pages = ""
        if user.search_mydealz:
            pages += "\nmydealz.de"
        if user.search_preisjaeger:
            pages += "\npreisjaeger.at"

        return (
            f"Folgende Websites werden durchsucht:"
            f"{pages}\n\n"
            f"Nutze /{BotCommand.SETTINGS} zum anpassen\n\n"
            f"Folgende Suchbegriffe sind aktiv:"
        )

    @staticmethod
    def help_msg() -> str:
        return textwrap.dedent(
            r"""
            <b><u>Suchbegriffe:</u></b>
            <b>-Groß- und Kleinschreibung werden nicht berücksichtigt
            - Leerzeichen werden entfernt
            - Standardmäßig wird ein Multi-Match verwendet</b>
            "<i>nutella&rewe</i>", "<i>Nutella & REWE</i>", und "<i>Nutella Rewe</i>" werden als "<i>nutella & rewe</i>" gespeichert und suchen nach Deals mit "Nutella" <b>und</b> "Rewe".

            <b>Um einen Suchbegriff auszuschließen nutze ein "!"</b>
            "<i>preisfehler & !lokal</i>" sucht nach "Preisfehler", schließt aber Ergebnisse mit "lokal" aus.

            <b>Für mehrere Suchbegriffe benutze ein ",":</b>
            "<i>Nutella, Ovomaltine</i>" sucht nach "Nutella" oder "Ovomaltine".

            <b>Um nach einem Leerzeichen zu suchen, benutze ein "+":</b>
            "<i>3060+TI</i>" liefert alle Deals mit "3060 TI" im Titel
            ("<i>3060 TI</i>" würde auch bei einem Deal mit dem Titel "RTX 3060 und Gra<b>ti</b>s Mauspad" anschlagen).

            <b>Um nach einem bestimmten Shop zu suchen, nutze eckige Klammern:</b>
            "<i>[Saturn], [Media+Markt]</i>" liefert alle Deals bei denen Saturn oder Media Markt als Händler hinterlegt ist.

            <b>Für eine Regex-Suche (case-sensitive), nutze r/:</b>
            "r/1\d{2} ?PS" liefert Deals mit z.B. "150 PS", "120PS", ...
            Für eine case-insensitive Regex-Suche nutze die Flag "/i".
            "r/1\d{2} ?PS/i" liefert Deals mit z.B. "100 PS", "150 ps", "120 Ps", "199 pS" ...
            Die Regex-Suche kann auch genutzt werden, um nach den reservierten Zeichen (+,&) für normale Queries zu suchen.
            Achte darauf, dass das "+" mit einem "\" escaped werden muss.
            Um z.B. nach Deals für eine Synology DS423+ zu suchen kann "r/ds423\+/i" genutzt werden.
            Zum lernen und testen von Regex empfehle ich https://regexr.com/

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
            mit /settings kann angepasst werden, welche Websites durchsucht werden sollen.
            """  # noqa: E501,
        )

    @staticmethod
    def query_instructions() -> str:
        return (
            "Bitte gebe eine Liste aus kommaseparierten Suchbegriffen ein."
            "\nGültige Zeichen: (Buchstaben, Zahlen - , + & ! [ ])"
            "\n/help für mehr Details"
            "\n/cancel zum abbrechen"
        )

    @staticmethod
    def invalid_query() -> str:
        return f"Der Suchbegriff ist ungültig!\n\n{Messages.query_instructions()}"

    @staticmethod
    def notification_added(notification: NotificationModel) -> str:
        return f"Suchbegriff angelegt\n\n{Messages.notification_overview(notification)}"

    @staticmethod
    def notification_overview(notification: NotificationModel) -> str:
        search_range = "Nur heiße Deals" if notification.search_hot_only else "Alle Deals"
        return (
            f"Suchbegriff: {notification.search_query}\n"
            f"Minimaler Preis: {str(notification.min_price) + ' €' if notification.min_price else '-'}\n"
            f"Maximaler Preis: {str(notification.max_price) + ' €' if notification.max_price else '-'}\n"
            f"Reichweite: {search_range}\n"
            f"Auch im Deal-Text suchen: {'Ja' if notification.search_description else 'Nein'}"
        )

    @staticmethod
    def query_updated(notification: NotificationModel) -> str:
        return f"Suchbegriff aktualisiert\n\n{Messages.notification_overview(notification)}"

    @staticmethod
    def price_instructions(price_type: str) -> str:
        return (
            f"Bitte gebe einen neuen {price_type}imal-Preis an.\n"
            f"/remove um den {price_type}imal-Preis zu löschen\n"
            "/cancel zum Abbrechen"
        )

    @staticmethod
    def invalid_price(price_type: str) -> str:
        return f"Der eingegebene Preis ist ungültig!\n\n{Messages.price_instructions(price_type)}"

    @staticmethod
    def notification_deleted(notification: NotificationModel) -> str:
        return f'Suchbegriff "{notification.search_query}" gelöscht'

    @staticmethod
    def deal_msg(deal: DealModel, notification: NotificationModel) -> str:
        message = (
            f'Neuer Deal für "{notification.search_query}":\n'
            f'<b><a href="{deal.link}">{html.escape(deal.full_title)}</a></b>\n'
            f"{html.escape(deal.description[0:300])}..."
        )

        if deal.price.amount:
            message += f"\n<b>Preis: {deal.price.amount:.2f} {deal.price.currency}</b>"

        return f"{message}{Messages.create_ref_link(deal.full_title)}"

    @staticmethod
    def create_ref_link(deal_title: str) -> str:
        if "topcashback" in deal_title.lower():
            return (
                "\n\nNoch keinen Topcashback-Account? "
                "Dann würde ich mich freuen, wenn Du meinen Reflink zum registrieren nutzt: "
                "https://www.topcashback.de/ref/weltraumpenner"
            )

        if "shoop" in deal_title.lower():
            return (
                "\n\nNoch keinen Shoop-Account? "
                "Dann würde ich mich freuen, wenn Du meinen Reflink zum registrieren nutzt: "
                "https://www.shoop.de/invite/1uk4VFUgHW"
            )

        if "ING" in deal_title and ("giro" in deal_title.lower() or "depot" in deal_title.lower()):
            return (
                "\n\nNoch kein ING-Konto? "
                "Dann würde ich mich freuen, wenn Du das Konto über meinen Reflink eröffnest."
                "\nGirokonto: https://www.ing.de/girokontokwk/a/yA8qP8JmyB"
                "\nExtra-Konto: https://www.ing.de/kwkaktion/a/a4ffd5C4yB"
                "\nDepot: https://www.ing.de/depotkwk/a/sc2gSj0qyB"
            )

        if "trade" in deal_title.lower() and "republic" in deal_title.lower():
            return (
                "\n\nNoch kein Trade Republic Depot? "
                "Dann würde ich mich freuen, wenn Du es über meinen Reflink eröffnest. "
                "https://ref.trade.re/1jp9gtlf"
            )

        return ""

    @staticmethod
    def add_notification_inconclusive(text: str) -> str:
        return f'Möchtest Du einen Suchbegriff für "{text}" erstellen?'

    @staticmethod
    def notification_not_found() -> str:
        return "Der Suchbegriff wurde bereits gelöscht."

    @staticmethod
    def user_not_whitelisted() -> str:
        return "Das ist ein Test-Bot. Offizieller Bot: @mydealz_notification_bot"

    @staticmethod
    def user_blacklisted() -> str:
        return "Du bist leider vom Bot blockiert worden. Tja. ¯\\_(ツ)_/¯"

    @staticmethod
    def broadcast_start() -> str:
        return "Was möchtest Du broadcasten?"

    @staticmethod
    def broadcast_verify() -> str:
        return "Möchtest Du diese Nachricht an alle Nutzer senden?"

    @staticmethod
    def broadcast_sent(amount_successful: int, amount_total: int) -> str:
        return f"Erfolgreich an {amount_successful}/{amount_total} Nutzer geschickt."
