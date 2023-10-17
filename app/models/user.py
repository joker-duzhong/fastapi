from typing import Optional

from odmantic import Model

# if TYPE_CHECKING:
#     from .item import Item  # noqa: F401


class User(Model):
    name: Optional[str]
    email: str
    password: str
    phone: str
    # items = relationship("Item", back_populates="owner")
