class GitHubProfileDto:
    user_id: str
    user_name: str
    image_url: str

    def __init__(self, user_id: str, user_name: str, image_url: str):
        self.user_id = user_id
        self.user_name = user_name
        self.image_url = image_url
        pass
