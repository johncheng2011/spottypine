from spotify import Spotify

def handler(event, context):
    spotify = Spotify()
    spotify.create_discover_weekkly_playlist()


if __name__ == "__main__":
    handler(None,None)
