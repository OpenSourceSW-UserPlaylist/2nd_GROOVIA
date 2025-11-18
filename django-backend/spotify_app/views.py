import os, requests
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .spotify_client import get_audio_features
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

class SpotifyLoginView(APIView):
    def get(self, request):
        scope = "user-read-private user-read-email"
        auth_url = (
            "https://accounts.spotify.com/authorize"
            f"?client_id={CLIENT_ID}"
            "&response_type=code"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope={scope}"
        )
        return redirect(auth_url)


class SpotifyCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        r = requests.post(token_url, data=data)
        r.raise_for_status()
        tokens = r.json()

        # access_token과 refresh_token 반환
        return Response(tokens)


class SpotifySearchView(APIView):
    def get(self, request):
        access_token = request.GET.get("token")
        query = request.GET.get("q", "IU")
        if not access_token:
            return Response({"error": "Missing access token"}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=5"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return Response(r.json())

class PingSpotifyView(APIView):
    def get(self, request):
        try:
            track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Uptown Funk 예시
            features = get_audio_features(track_id)
            return Response({
                "message": "Spotify API reachable ✅",
                "track_id": track_id,
                "tempo": features.get("tempo"),
                "energy": features.get("energy"),
                "danceability": features.get("danceability"),
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PingView(APIView):
    def get(self, request):
        return Response({"message": "pong"})

