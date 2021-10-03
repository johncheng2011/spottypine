import datetime
from functools import cached_property

import boto3
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from ssm_cache_handler import SSMCacheHandler


class Spotify(spotipy.Spotify):
    def __init__(self):
        ssm = boto3.client("ssm")
        SPOTIFY_CLIENT_ID=ssm.get_parameter(Name="SPOTIFY_CLIENT_ID")["Parameter"]["Value"]
        SPOTIFY_CLIENT_SECRET=ssm.get_parameter(Name="SPOTIFY_CLIENT_SECRET")["Parameter"]["Value"]
        SPOTIFY_REDIRECT_URI=ssm.get_parameter(Name="SPOTIFY_REDIRECT_URI")["Parameter"]["Value"]
        scope = "playlist-modify-private playlist-read-private user-read-recently-played playlist-modify-public"
        super().__init__(
            auth_manager=SpotifyOAuth(
                scope=scope,
                cache_handler=SSMCacheHandler(ssm),
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
            )
        )

    @cached_property
    def discover_weekly_id(self):
        discover_weekly_playlist = self.find_playlist("Discover Weekly")
        return (
            "" if discover_weekly_playlist is None else discover_weekly_playlist["id"]
        )

    def find_playlist(self, playlist_name):
        playlists = self.current_user_playlists().get("items", [])
        for playlist in playlists:
            if playlist["name"] == playlist_name:
                return playlist

    @cached_property
    def discover_weekly_tracks(self):
        try:
            return self.playlist_tracks(self.discover_weekly_id)["items"]
        except spotipy.exceptions.SpotifyException:
            return []

    def create_playlist(self, playlist_name):
        playlist = self.find_playlist(playlist_name)
        return (
            playlist
            if playlist
            else self.user_playlist_create(
                self.current_user()["id"], playlist_name, public=False
            )
        )

    def create_discover_weekkly_playlist(self):
        new_playlist = self.create_playlist(f"{self.start_of_week} discover weekly")
        self.playlist_replace_items(
            new_playlist["id"],
            [track["track"]["id"] for track in self.discover_weekly_tracks],
        )

    @property
    def start_of_week(self):
        now = datetime.datetime.now()
        monday = now - datetime.timedelta(days=now.weekday())
        return monday.strftime("%m/%d/%y")
