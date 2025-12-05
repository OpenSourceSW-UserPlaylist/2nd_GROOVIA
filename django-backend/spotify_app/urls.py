from django.urls import path
from .views import UrlProcessView, AppleRecommendView

urlpatterns = [
    # A 모드: Flutter URL → track_id → 추천
    path('process-urls/', UrlProcessView.as_view(), name='process_urls'),

    # B 모드: 브라우저 GET 테스트용 (기본 3곡 자동 추천)
    path('apple-test/', AppleRecommendView.as_view(), name='apple_test'),
]
