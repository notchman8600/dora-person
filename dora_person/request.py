# 面倒なのでリクエストのモデルとDTOを全部定義


# Standard Library
from urllib.parse import unquote


class SubmitDoraPersonRequestDto:
    """_summary_
    銅鑼パーソンの立候補リクエストDTO
    """

    user_name: str
    avatar_url: str
    message: str

    def __init__(self, name: str, message: str, avatar_url: str):
        self.user_name = name
        self.message = message
        self.avatar_url = unquote(avatar_url)
