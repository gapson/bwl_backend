from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.admin import FlatPageAdmin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from content.models import *
# Register your models here.

class AppSettingAdmin(admin.ModelAdmin):

    list_display = ('name', 'home_page_image', 'login_image', 'registration_image')
    search_fields = ('home_page_image', 'login_image', 'registration_image')
    
admin.site.register(AppSetting, AppSettingAdmin)

class PageAdmin(TranslationAdmin):

    list_display = ('url', 'title', 'type')
    list_filter = ('sites', 'registration_required')
    search_fields = ('url', 'title')
    
admin.site.unregister(FlatPage)
admin.site.register(Page, PageAdmin)

class ProfileUserInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Additional Properties'

class TransactionForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        #self.fields['transaction_ref_model'].queryset = ContentType.objects.filter(app_label='content')

class CreditInline(admin.StackedInline):
    model = Credit
    fields = ('balance', )
    verbose_name_plural = 'User Credit'
    extra = 0
        
class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    form = TransactionForm
    list_display = ('user', 'credit_setting', 'amount_paid', 'currency', 'deposit', 'withdraw', 'transaction_type')
    
admin.site.register(Transaction, TransactionAdmin)
    
class UserAdmin(UserAdmin):
    inlines        = (ProfileUserInline, CreditInline)
    #list_display= ('username','email','first_name','last_name','is_staff','is_active','get_file_browser_access','get_groups')
    #list_filter    = ('is_staff','is_superuser','is_active','groups','extendeduser__allowed_department','extendeduser__allowed_section','extendeduser__is_advisor', 'extendeduser__is_recruiter','extendeduser__file_browser_access')
    
def user_unicode(self):
    if self.last_name=='' and self.first_name=='':
        name= self.username
    else:
        name = '%s %s (%s)' % (self.first_name, self.last_name,  self.username)
    return  name

User.__str__ = user_unicode
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
       
class ArtistAdmin(admin.ModelAdmin):
    list_display    = ('name', )

admin.site.register(Artist, ArtistAdmin) 

class SubscriptionAdmin(admin.ModelAdmin):
    list_display= ('user','offer','offer_price', 'currency','date_start','date_end',
                   'payment_date','is_active')
    list_filter    = ('user','offer','currency','date_start','date_end','payment_date','is_active')
    
admin.site.register(Subscription, SubscriptionAdmin)

class CurrencyAdmin(admin.ModelAdmin):
    list_display    = ('name', 'region_name','countries_list')
    list_filter    = ('name', 'region_name')
    search_fields = ('name', 'region_name')
    filter_horizontal = ('country', )
    
    def countries_list(self, obj):
        return ','.join([c.name for c in obj.country.all()])
    countries_list.short_description = 'Countries List'
    countries_list.allow_tags = True
        admin.site.register(Currency, CurrencyAdmin) 

class CreditSettingAdmin(admin.ModelAdmin):
    list_display    = ('currency', 'value_in_currency', 'credit', 'date_start', 'date_end', 'is_active')

admin.site.register(CreditSetting, CreditSettingAdmin) 

class PriceInline(admin.StackedInline):
    model = Price
    fields = ('credit', 'is_active' , 'date_start', 'date_end')
    verbose_name_plural = 'Offer Prices'
    verbose_name = 'Offer Price'
    extra = 0
    

class MediaInline(TranslationStackedInline):
    inlines = (PriceInline, )
    model = Media
    verbose_name_plural = 'Media'
    extra = 0
    show_change_link = True
    
class MediaAdmin(TranslationAdmin):
    inlines = (PriceInline, )
    list_display    = ('title', 'type', 'author', 'duration', 'published_date', 'message')

admin.site.register(Media, MediaAdmin)
class MessageForm(forms.ModelForm):
    message_offers = forms.ModelMultipleChoiceField(
        queryset=Offer.objects.all(),  label=_('Offer'),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Offer'),
            is_stacked=False
        )
    )
    
    class Meta:
        model = Message
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['message_offers'].initial = self.instance.message_offers.all()

    def save(self, commit=True):
        message = super(MessageForm, self).save(commit=False)

        if message.pk:
            message.message_offers.set(self.cleaned_data['message_offers'])
            self.save_m2m()
        return message
        
class MessageOfferInline(admin.TabularInline):
    model = Offer.message.through
    verbose_name_plural = 'Offers'
    verbose_name = 'Offers'
    
class MessageAdmin(admin.ModelAdmin):
    inlines        = (MediaInline, )
    form = MessageForm
    list_display = ('code', 'reference', 'published_date', 'is_active')
    list_filter    = ('code','reference', 'published_date', 'is_active')
    search_fields = ('code', 'reference', 'published_date')
    filter_horizontal = ('users', )
    read_only = ('is_active', )
    
    fieldsets = (
        ('General Information', {
            'classes': ('grp-collapse grp-open',),
            'description': 'General information',
            'fields': ('code', 'reference', 'published_date', 'is_active')
        }),
        #('Medias', {
            #'classes': ('grp-collapse grp-open',),
            #'description': 'Offer',
            #'fields': ('MediaInline',)
        #}),
        ('Offers', {
            'classes': ('grp-collapse grp-open',),
            'description': 'Offer',
            'fields': ('message_offers',)
        }),
        ('Users', {
            'classes': ('grp-collapse grp-open',),
            'description': 'user',
            'fields': ('users', )
        }),
    )

admin.site.register(Message, MessageAdmin) 

class OfferAdmin(TranslationAdmin):
    inlines = (PriceInline, )
    list_display = ('name', 'duration', 'is_free', 'auto_assign', 'is_sharable', 'is_renewable', 'is_active')
    list_editable = ('duration', 'is_free', 'auto_assign', 'is_sharable', 'is_renewable', 'is_active')
    list_filter    = ('is_free', 'is_active', 'auto_assign', 'is_sharable', 'is_renewable')
    search_fields = ('name', )
    filter_horizontal = ('message', 'media')
    
    fieldsets = (
        (_('General information'), {
            'classes': ('grp-collapse grp-open',),
            'description': _('General information'),
            'fields': ('name', 'is_active', 'is_free', 'auto_assign', 'is_sharable', 
                       'is_renewable', 'duration',)
        }),
        (_('Description'), {
            'classes': ('grp-collapse grp-open',),
            'description': _('Offer'),
            'fields': ('description',)
        }),
        (_('Message'), {
            'classes': ('grp-collapse grp-open',),
            'description': 'Message',
            'fields': ('message',)
        }),
        (_('Additional Media'), {
            'classes': ('grp-collapse grp-open',),
            'description': _('Additional Media'),
            'fields': ('media',)
        }),
    )

admin.site.register(Offer,OfferAdmin) 

class PlaylistAdmin(admin.ModelAdmin):
    list_display= ('name','user',)
    list_filter    = ('name','user',)
    filter_horizontal = ('media',)
admin.site.register(Playlist, PlaylistAdmin)

class UserAlarmSettingsAdmin(admin.ModelAdmin):
    list_display= ('user','date_start', 'date_end', 'time')
    list_filter    = ('user','date_start', 'date_end')
    
admin.site.register(UserAlarmSettings, UserAlarmSettingsAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display= ('user','date', 'music', 'message', 'msg_listen')
    list_filter    = ('user','date', 'music', 'message')
    
admin.site.register(Notification, NotificationAdmin)

class ReferralAdmin(admin.ModelAdmin):
    list_display= ('user','referred_user', 'date')
    list_filter    = ('user',)
    
admin.site.register(Referral, ReferralAdmin)

class SharedItemlAdmin(admin.ModelAdmin):
    list_display= ('from_user','to_user', 'date', 'expiration_date')
    list_filter    = ('from_user', 'to_user', 'date', 'expiration_date')
    
admin.site.register(SharedItem, SharedItemlAdmin)

class TestimonyAdmin(admin.ModelAdmin):
    list_display= ('user','user_name', )
    list_filter    = ('user', 'user_name')
    
admin.site.register(Testimony, TestimonyAdmin)

class ThemeSuggestionsAdmin(admin.ModelAdmin):
    list_display= ('user', )
    list_filter    = ('user',)
    
admin.site.register(ThemeSuggestions, ThemeSuggestionsAdmin)