class NotificationNotFoundError(Exception):
    def __init__(self, notification_id: int) -> None:
        super().__init__(f'Notification with ID "{notification_id}" not found')


class UserNotFoundError(Exception):
    def __init__(self, user_id: int) -> None:
        super().__init__(f'User with ID "{user_id}" not found')


class TooManyNotificationsError(Exception):
    def __init__(self, user_id: int) -> None:
        super().__init__(f'Notification Cap reached by: {user_id}')
