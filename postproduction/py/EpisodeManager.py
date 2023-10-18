class EpisodeManager:
    @staticmethod
    def validate_episode(data, episode_type, episode_number):
        number = data["Number"]
        if episode_number:
            if episode_number != number:
                raise ValueError(
                    f"Episode number mismatch: {episode_number} != {number}"
                )
        else:
            if episode_type != number:
                raise ValueError(f"Episode name mismatch: {episode_type} != {number}")

    @staticmethod
    def format_title(data):
        number, title, starr = data["Number"], data["Title"], ", ".join(data["Starr"])
        return (
            f"#{number} {title} ({starr})"
            if number.isdecimal()
            else f"{title} ({starr})"
        )

    @staticmethod
    def format_comments(topics):
        return "<ol>" + "".join([f"<li>{t}</li>" for t in topics]) + "</ol>"

    @staticmethod
    def format_comments_sns(topics):
        return "\n".join([f"{i + 1}. {topic}" for i, topic in enumerate(topics)])

    @staticmethod
    def create_sns_post(data):
        title = EpisodeManager.format_title(data)
        contents = EpisodeManager.format_comments_sns(data["Topics"])
        return f"""{title}

{contents}

#コンキャスト #concast
🙌視聴はこちらから https://linktr.ee/concastx"""
