import logging

from src.db.notification_client import NotificationClient
from src.db.user_client import UserClient
from src.exceptions import UserNotFoundError
from src.models import UserModel

logger = logging.getLogger(__name__)


def update_user_id(user: UserModel, new_id: int) -> UserModel:
    try:
        new_user = UserClient.fetch(new_id)
    except UserNotFoundError:
        pass
    else:
        logger.info("Can not migrate user-id from %s to %s. New id already exists. Delete old user.")
        UserClient.delete(user.id)

        return new_user

    NotificationClient.update_user_id(user.id, new_id)

    return UserClient.update_user_id(user, new_id)
