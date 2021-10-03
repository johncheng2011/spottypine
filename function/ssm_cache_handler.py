import json

from spotipy.cache_handler import CacheHandler


class SSMCacheHandler(CacheHandler):
    def __init__(self, ssm_client):
        self.ssm = ssm_client

    def get_cached_token(self):
        token_info = None

        token_info_string = self.ssm.get_parameter(Name="spotify_token_info")["Parameter"]["Value"]
        token_info = json.loads(token_info_string)

        return token_info


    def save_token_to_cache(self, token_info):
        self.ssm.put_parameter(Name="spotify_token_info", Value=json.dumps(token_info), Type="String", Overwrite=True)
