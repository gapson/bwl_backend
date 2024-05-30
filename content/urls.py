from rest_framework.routers import DefaultRouter
from django.conf.urls import url, re_path
from django.contrib.auth import get_user_model

from content import views


router = DefaultRouter()
router.register("discorvery-pages", views.DiscorveryPagesViewSet, basename='discorvery-pages')
router.register(r"user-alarm-setting", views.UserAlarmSettingsAPIView, basename='user_alarm_setting')
router.register(r"currency", views.CurrencyAPIView, basename='currency')
router.register(r"country", views.CountryAPIView, basename='country')
router.register(r"playlist", views.PlaylistAPIView, basename='playlist')
router.register(r"offer", views.OfferAPIView, basename='offer')
router.register(r"subscription/get_user_messages", views.UserMessagesAPIView, basename='get_user_messages')
router.register(r"subscription/get_user_medias", views.UserMediaAPIView, basename='get_user_messages')
router.register(r"subscription", views.SubscriptionAPIView, basename='subscription')
router.register(r"user-credit", views.UserCreditAPIView, basename='user_credit')
router.register(r"theme-suggestion", views.ThemeSuggestionsAPIView, basename='theme_suggestion')
router.register(r"user-transaction", views.TransactionAPIView, basename='user_transaction')
#router.register(r"transaction", views.TransctionAPIView, basename='transaction')

#router.register("users", views.UserViewSet)

#User = get_user_model()

#urlpatterns = [
    #re_path(r"^setting?", views.SettingDataViewSet.as_view({'get':'retrieve'}), name="yooo"),
    #]
#[re_path(r"^setting?", views.DiscorveryPagesViewSet.as_view(), name="login"),]
urlpatterns = router.urls