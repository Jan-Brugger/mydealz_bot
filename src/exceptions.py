class NotificationNotFoundError(Exception):
    def __init__(self, user_id: int):
        super().__init__("No notification with id %s", user_id)


class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        super().__init__("No user with id %s", user_id)
