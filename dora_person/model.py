class DoraPerson:
    name: str
    message: str
    avatar_url: str
    count: int

    def __init__(self, name, message, avatar_url, count: int = 0):
        self.name = name
        self.message = message
        self.avatar_url = avatar_url
        self.count = count
