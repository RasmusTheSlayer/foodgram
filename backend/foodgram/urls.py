from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)
from api.utils import redirect_short_link

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path(
        'r/<str:short_code>/',
        redirect_short_link,
        name='short-link-redirect'
    ),
    path('api/docs/schema/',
         SpectacularAPIView.as_view(),
         name='schema'),
    path('api/docs/redoc/',
         SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
    path('api/docs/openapi-schema.yml',
         SpectacularAPIView.as_view(),
         name='schema-yml'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
