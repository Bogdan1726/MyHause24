from django.urls import path
from .views import SummaryListView, ProfileDetailView, ProfileUpdateView

urlpatterns = [
    path('', SummaryListView.as_view(), name='cabinet'),

    # region profile
    path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='update_profile'),
    # endregion profile
]
