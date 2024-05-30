from random import randint
from datetime import timedelta
from django.db import models

# Create your models here.
from cities_light.models import Country

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.db.models import Max, Q, F, Prefetch

attr_exist = lambda name: hasattr(settings, name)

class TimeStampedModel(models.Model):
    """ TimeStampedModel
    An abstract base class model that provides self-managed "created" and
    "modified" fields.
    """
    date_time    = timezone.now
    created     = models.DateTimeField(verbose_name=_('Created Date'), default=date_time, editable=False)
    modified     = models.DateTimeField(verbose_name=_('Modified Dtae'), default=date_time, editable=False)

    class Meta:
        get_latest_by = 'created'
        #ordering = ('-modified', '-created',)
        abstract = True
        ordering = ('created', )
    
    def save(self, *args, **kwargs):
        if kwargs.get('no_modified', False):
            del kwargs['no_modified']
        else:
            self.modified = timezone.now()
        return super(TimeStampedModel, self).save(*args, **kwargs)
 
 
class PasswordResetCode(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='password_reset_users', 
                    on_delete=models.CASCADE)
    uid = models.CharField(max_length=20, verbose_name=_('Uid Name'),)
    token = models.CharField(max_length=100, verbose_name=_('Token'),)
    expiration_date = models.DateTimeField(verbose_name=_('Expiration Date'), )
    code = models.CharField(max_length=20, verbose_name=_('Code'),)
    succes = models.BooleanField(verbose_name=_('Succes'), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is Active'), default=True)
    attempt = models.IntegerField(verbose_name=_('Number of Attempt'), default=0)
    
    @classmethod
    def random_with_N_digits(cls, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)
    
    def save(self, *args, **kwargs):
        if not self.code:
            
            length = attr_exist('BWL_PASSWORD_RESET_CODE_LENGTH') and settings.BWL_PASSWORD_RESET_CODE_LENGTH or 6
            code = self.random_with_N_digits(length)
            self.code = code 
            expiration = attr_exist('BWL_PASSWORD_RESET_CODE_EXPIRATION') and \
                settings.BWL_PASSWORD_RESET_CODE_EXPIRATION or timedelta(minutes=5)#should be a timedelta
            self.expiration_date = self.created+expiration
        elif self.pk:
            max_attempt = attr_exist('BWL_PASSWORD_RESET_CODE_MAX_ATTEMPT') and \
                settings.BWL_PASSWORD_RESET_CODE_MAX_ATTEMPT or 3
            self.attempt +=1
            if self.attempt>max_attempt or self.succes:
                self.is_active = False
        
        return super().save(*args, **kwargs)
        
class FlatPageExt(FlatPage, TimeStampedModel):
    
    def get_default_order():
        max = 0
        try:
            max = Page.objects.all().aggregate(Max('display_order'))['display_order']
            if not max:
                max = 0
        except:
            pass
        return max + 1
    
    class Meta:
        abstract = True
        ordering = ('display_order', 'title')
        
    display_order        = models.IntegerField(verbose_name='Display Order', default=get_default_order,
                            help_text='Used to order the display', blank=True, null=True)

class Page(FlatPageExt):
    DISCOVER = 'discover'
    TYPE = ((DISCOVER,_('Display in Discover section')),)
    
    type = models.CharField(verbose_name=_('Page Type'), choices=TYPE, max_length=50, blank=True, null=True)
    
class AppSetting(TimeStampedModel):
    name =  models.CharField(max_length=100, verbose_name=_('Name'), default='Default Setting', editable=False)
    home_page_image = models.ImageField(upload_to='catalog/images', verbose_name=_('Home Page Image'), 
                                        null=True, blank=True)
    login_image = models.ImageField(upload_to='catalog/images', verbose_name=_('Login Image'), 
                                        null=True, blank=True)
    registration_image = models.ImageField(upload_to='catalog/images', verbose_name=_('Registration Image'), 
                                        null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Settings")
        verbose_name = _("Setting")
        unique_together = ('name', )  

class Currency(TimeStampedModel):
    name = models.CharField(max_length=250, verbose_name=_('Currency Name'),)
    region_name = models.CharField(max_length=250, verbose_name=_('Region Name'), null=True, blank=True)
    country = models.ManyToManyField(Country, verbose_name=_('Country'), related_name='currencies')
    
    class Meta:
        verbose_name_plural = "currencies/Region"
        ordering = ('name', )
    
    def __str__(self):
        return '%s (%s)' % (self.region_name and self.region_name or '', self.name)
    
class CreditSetting(TimeStampedModel):
    currency = models.ForeignKey(Currency, verbose_name=_('Region/Currency'), related_name='currency_credits_setting', 
                    on_delete=models.CASCADE)
    value_in_currency = models.FloatField(verbose_name=_('Value In Currency'), default=1)
    credit = models.FloatField(verbose_name=_('Number of Credit'))
    is_active = models.BooleanField(verbose_name=_('Is active?'), default=True, 
            help_text=_('UnCheck this box if this credit setting is not available anymore'))
    date_start = models.DateTimeField(verbose_name=_('Date Start'), null=True, blank=True)
    date_end = models.DateTimeField(verbose_name=_('Date End'), null=True, blank=True)
    
    def __str__(self):
        return f'{self.value_in_currency} {self.currency.name}->{self.credit} credit'
    
class Profile(TimeStampedModel):
    MASCULIN = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER = ((MASCULIN, MASCULIN), (FEMALE, FEMALE), (OTHER, 'Other'))
    
    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE, related_name='profile')
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.SET_NULL, 
                                blank=True, null=True)
    default_currency = models.ForeignKey(Currency, verbose_name=_('Default Currency'), 
                        on_delete=models.SET_NULL, blank=True, null=True)
    uid = models.CharField(max_length=250, verbose_name=_('UID'), blank=True, null=True)
    phone_number = models.CharField(max_length=30, verbose_name=_('Phone Number'), blank=True, null=True)
    language = models.CharField(verbose_name=_('Language'), choices=settings.LANGUAGES, 
                                max_length=10, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_('Birth Date'), blank=True, null=True)
    gender = models.CharField(verbose_name=_('Gender'), choices=GENDER, blank=True, null=True, max_length=10)
    
    def __str__(self):
        return str(self.user)
    
    def save(self, *args, **kwargs):
        if not self.id:
            #create free subcription for the new user
            data = {'user':self.user}
            Subscription.create_subscription(data, create_free=True)
        return super().save(*args, **kwargs)
    
class Artist(TimeStampedModel):
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    
    
    def __str__(self):
        return str(self.name)

class Message(TimeStampedModel):
    code = models.CharField(max_length=20, verbose_name=_('Code'),)
    reference = models.CharField(max_length=50, verbose_name=_('Reference'),)
    published_date = models.DateField(verbose_name=_('Published Date'), default=timezone.now)
    users = models.ManyToManyField(User, verbose_name=_('Users'), related_name='messages', blank=True,
            help_text="Use this field to assign Users to messages. Note: if a message is assigned to a user, it won't be available to other users")
    is_active = models.BooleanField(verbose_name=_('Is Active'), default=False)
    
    class Meta:
        verbose_name_plural = _("Messages")
        ordering = ('code', )
    
    def __str__(self):
        return '%s ' % (self.code, )
    
    @classmethod
    def get_user_messages(self, user, today=False):
        current_date_time = published_date=timezone.now()
        filter = {'message_offers__offer_subscription__user': user, 
            'message_offers__offer_subscription__date_start__lte': current_date_time, 
            'message_offers__offer_subscription__date_end__gte':current_date_time}
        user_messages = Message.objects.filter(**filter).prefetch_related('medias').order_by('published_date')
        if today:
            user_messages = user_messages.filter(published_date=current_date_time.date())
        return user_messages

class MediaManager(models.Manager):
    
    def include_current_price(self):
        current_time = timezone.now()
        p = Price.objects.filter(is_active=True).order_by('modified')
        p = p.filter(Q(date_start__isnull=True) | Q(date_start__lte=current_time))
        p = p.filter(Q(date_end__isnull=True) | Q(date_end__gte=current_time))
        return self.filter().prefetch_related(Prefetch('media_prices', queryset=p, to_attr='prices'))
    
class Media(TimeStampedModel):
    '''
        Model class to define different type of Media: can be a Message, Instrument or Music
    '''
    
    objects = MediaManager()
    
    MESSAGE = 'message'
    INSTRUMENT = 'Instrument'
    MUSIC = 'music'
    
    MEDIA_TYPE = (
        (INSTRUMENT, _('Instrument')), 
        (MESSAGE, _('Message')), 
        (MUSIC, _('Music'))
    )
    message = models.ForeignKey(Message, verbose_name=_('Message'), related_name='medias', 
                    on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_('Title'),)
    type = models.CharField(verbose_name=_('Media Type'), choices=MEDIA_TYPE, max_length=30)
    author = models.ForeignKey(Artist, verbose_name=_('Author'), related_name='artist_medias', on_delete=models.SET_NULL, blank=True, null=True)
    duration = models.FloatField(verbose_name=_('Duration'))
    published_date = models.DateField(verbose_name=_('Published Date'), default=timezone.now)
    url_link = models.CharField(max_length=255, verbose_name=_('External Url'), 
        blank=True, null=True, 
        help_text=_('Use this field if the Music file is store externally to this application'))
    internal_link = models.FileField(upload_to='catalog/music', verbose_name=_('Music File'), 
                        help_text=_('Use this field if the Music file is store Internally to this application'), 
                        blank=True, null=True)    
    is_shareable = models.BooleanField(verbose_name=_('Can be shared'), 
                help_text=_('Check this field if the music can be shared'))
    is_downloadable = models.BooleanField(verbose_name=_('Can be downloaded'), 
                help_text=_('Check this field if the music can be downloaded'))
    is_free = models.BooleanField(verbose_name=_('Is Free'), 
                help_text=_('Check this field if the music is free'))
    is_active = models.BooleanField(verbose_name=_('Is Active'), 
                help_text=_('Check this field if the music is active'), default=True)
    copyright_info = models.TextField(verbose_name=_('Copyright Information'), blank=True, null=True)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True, 
                    help_text=_('Provide a brief description about the Music'))
    image = models.ImageField(upload_to='catalog/images', verbose_name=_('Audio Player background image'), blank=True, null=True,
                            help_text=_('Use this field to set the image that will be displayed in the media player'))  
    
    class Meta:
        #verbose_name_plural = _("Medias")
        ordering = ('published_date', )
        
    
    def __str__(self):
        return '%s (%s)' % (self.title, self.author and self.author or '')
    
    @classmethod
    def get_user_medias(cls, user, filter={}):
        current_date_time = published_date=timezone.now()
        filter.update({'message__message_offers__offer_subscription__user': user, 
            'message__message_offers__offer_subscription__date_start__lte': current_date_time, 
            'message__message_offers__offer_subscription__date_end__gte':current_date_time})
        user_media = cls.objects.include_current_price().filter(**filter).order_by('published_date')
        return user_media
    
class Playlist(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'),)
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_playlists', 
                    on_delete=models.CASCADE)
    media = models.ManyToManyField(Media, verbose_name=_('Media'), related_name='media_playlists', blank=True)
    
    
    class Meta:
        verbose_name_plural = _("Playlist")
        ordering = ('name', )
        unique_together = ("user", "name")
    
    def __str__(self):
        return '%s ' % (self.name, )
    
class OfferManager(models.Manager):
    def current(self, my_date):
        return super(OfferManager, self).get_query_set().filter(created__lte=my_date)
    
    def include_current_price(self):
        current_time = timezone.now()
        p = Price.objects.filter(is_active=True).order_by('modified')
        p = p.filter(Q(date_start__isnull=True) | Q(date_start__lte=current_time))
        p = p.filter(Q(date_end__isnull=True) | Q(date_end__gte=current_time))
        return self.filter().prefetch_related(Prefetch('offer_prices', queryset=p, to_attr='prices'))
    
class Offer(TimeStampedModel):
    objects = OfferManager()
    
    name = models.CharField(max_length=255, verbose_name=_('Name'),)
    is_active = models.BooleanField(verbose_name=_('Is active?'), default=True, 
            help_text=_('UnCheck this box if this offer is not available anymore'))
    is_free = models.BooleanField(verbose_name=_('Is Free?'), default=False, 
            help_text=_('Check this box if this offer is free'))
    auto_assign = models.BooleanField(verbose_name=_('Auto Assign?'), default=False, 
            help_text=_('Check this box if this offer should be automatically assigned to new user'))
    is_sharable = models.BooleanField(verbose_name=_('Is Sharable?'), default=False, 
            help_text=_('Check this box if the messages and media in this offer can be shared with other user'))
    is_renewable = models.BooleanField(verbose_name=_('Is Renewable?'), default=True, 
            help_text=_('Check this box if this offer can be renew'))
    duration = models.IntegerField(verbose_name=_('Offer Duration (In day)'),  
                    help_text=_('In Day, 0 for unlimited'))
    message = models.ManyToManyField(Message, verbose_name=_('Message'), 
                                     related_name='message_offers', blank=True)
    media = models.ManyToManyField(Media, verbose_name=_('Media'), 
                                     related_name='media_offers', blank=True)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    
    class Meta:
        verbose_name_plural = _("Offers")
        ordering = ('name', )
    
    def __str__(self):
        return '%s ' % (self.name, )
    
    def get_current_price(self, currency):
        current_time = timezone.now()
        p = self.offer_prices.all().filter(currency=currency, is_active=True).order_by('modified')
        p = p.filter(Q(date_start__is_null=False) | Q(date_start__lte=current_time))
        p = p.filter(Q(date_end__is_null=False) | Q(date_end__gte=current_time))
        return p.count()>0 and p[0] or None
    
class Price(TimeStampedModel):
    credit = models.FloatField(verbose_name=_('Number of credit'))
    offer = models.ForeignKey(Offer, verbose_name=_('Offer'), related_name='offer_prices', 
                    on_delete=models.CASCADE, null=True, blank=True)
    media = models.ForeignKey(Media, verbose_name=_('Media'), related_name='media_prices', 
                    on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active?'), default=True, 
            help_text=_('UnCheck this box if this price is not available anymore'))
    date_start = models.DateTimeField(verbose_name=_('Date Start'), null=True, blank=True)
    date_end = models.DateTimeField(verbose_name=_('Date End'), null=True, blank=True)    
    
    class Meta:
        verbose_name_plural = _("Prices")
        ordering = ('date_start', )
    
    def __str__(self):
        return '%s (%s credits)' % (self.offer and self.offer.name or self.media.name, self.credit)
    
class Credit(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_credits', 
                    on_delete=models.CASCADE)
    balance = models.FloatField(verbose_name=_('Balance'), null=True, blank=True, default=0)
    
class Transaction(TimeStampedModel):
    TYPE_SUBSCRIPTION = 'Subscription'
    TYPE_MEDIA = 'Media'
    TYPE_CREDIT = 'credit'
    TYPE = ((TYPE_SUBSCRIPTION, 'Subscription'),
            (TYPE_MEDIA, 'Media'),
            (TYPE_CREDIT, 'Credit'))
    
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_transactions', 
                    on_delete=models.CASCADE)
    credit_setting = models.ForeignKey(CreditSetting, verbose_name=_('Credit Setting'), 
            related_name='crdit_setting_transactions', blank=True, null=True, on_delete=models.SET_NULL)
    
    amount_paid = models.FloatField(verbose_name=_('Amount Paid'), default=0)
    deposit = models.FloatField(verbose_name=_('Deposit credit'))
    withdraw = models.FloatField(verbose_name=_('Withdrawal credit'))
    transaction_date = models.DateTimeField(verbose_name=_('Transaction Date'), default=timezone.now)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), related_name='currency_transaction', on_delete=models.DO_NOTHING, 
                                 blank=True, null=True)
    transaction_ref_id = models.IntegerField(verbose_name=_('Transaction Reference Id'), blank=True, null=True)
    transaction_type = models.CharField(verbose_name=_('Transaction Type'), max_length=20, choices=TYPE, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = _("Transaction")
        ordering = ('-created', )
        
    @property
    def transaction_model(self):
        if self.transaction_type and self.transaction_ref_id:
            try:
                cls = eval(self.transaction_type)
                return cls.objects.get(id=self.transaction_ref_id)
            except Exception as e:
                return None
    @property
    def get_reference(self):
        ref = ''
        if hasattr(self.transaction_model, 'offer'):
            ref = self.transaction_model.offer.name
        elif hasattr(self.transaction_model, 'title'):
            ref = self.transaction_model.title
        return ref
    
    @property
    def get_type(self):
        type = ''
        if self.transaction_type==self.TYPE_SUBSCRIPTION:
            type = 'Subscription Purchase'
        elif self.transaction_type==self.TYPE_CREDIT:
            type = 'Credit Recharge'
        elif self.transaction_type==self.TYPE_MEDIA:
            type = 'Media Purchase'
        return type
    
    def __str__(self):
        return '%s ' % (self.user, )
    
    def save(self, *args, **kwargs):
        """
        Override Save method To update User credit on each transaction
        """
        result =  super().save(*args, **kwargs)
        if self.user:
            user_credit, created = Credit.objects.get_or_create(user=self.user)
            if self.deposit>0:
                user_credit.balance +=self.deposit
            if self.withdraw>0:
                user_credit.balance -=self.withdraw
            user_credit.save()
        return result
        
class Subscription(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_subscriptions', 
                    on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, verbose_name=_('Offer'), related_name='offer_subscription', 
                    on_delete=models.CASCADE)
    offer_price = models.ForeignKey(Price, verbose_name=_('Offer Price'), related_name='subscriptions', 
                    on_delete=models.CASCADE, null=True, blank=True)
    price = models.FloatField(verbose_name=_('Price'), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active?'), default=True, 
            help_text=_('UnCheck this box if this subscription is not available anymore'))
    date_start = models.DateTimeField(verbose_name=_('Date Start'))
    date_end = models.DateTimeField(verbose_name=_('Date End'), null=True, blank=True)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), related_name='currency_subscription', 
                    on_delete=models.SET_NULL, null=True, blank=True)
    payment_date = models.DateTimeField(verbose_name=_('Payment Date'), null=True, blank=True)
    
    class Meta:
        verbose_name_plural = _("Subscriptions")
        ordering = ('date_start', )
    
    def __str__(self):
        return '%s (%s)' % (self.offer.name, self.price)
    
    def save(self, *args, **kwargs):
        if not self.date_end:
            self.date_end = self.date_start + timedelta(days=self.offer.duration)
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_user_subscription(cls, user, current=False):
        current_date_time = timezone.now()
        subscriptions = cls.objects.filter(user=user, date_start__lte=current_date_time).order_by('date_end')
        if current:
            subscriptions = subscriptions.filter(date_end__gte=current_date_time)
        return subscriptions.prefetch_related('offer', 'offer__message', 'offer__media')
    
    @classmethod
    def create_subscription(cls, data, create_free=False):
        #create free subcription for the new user
        # data contains: user, offer, offer_price, price, date_start, payment_date
        if 'date_start' not in data:
            data['date_start'] = timezone.now()
        if create_free:
            offer = Offer.objects.filter(is_active=True, is_free=True, auto_assign=True)
            if offer.count()>0:
                data['offer'] = offer[0]
        try:
            r = cls.objects.create(**data)
        except Exception as e:
            print('-->>>create_subscription error', e)
            r = None
        return r

class UserAlarmSettings(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_alarm_settings', 
                            on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=True, blank=True)
    date_start = models.DateField(verbose_name=_('Date Start'), null=True, blank=True)
    date_end = models.DateField(verbose_name=_('Date End'), null=True, blank=True)
    time = models.TimeField(verbose_name=_('Time'), null=True, blank=True)
    monday = models.BooleanField(verbose_name='Monday', blank=True, null=True)
    tuesday = models.BooleanField(verbose_name=_('Tuesday'), blank=True, null=True)
    wednesday = models.BooleanField(verbose_name=_('Wednesday'), blank=True, null=True)
    thursday = models.BooleanField(verbose_name=_('Thursday'), blank=True, null=True)
    friday = models.BooleanField(verbose_name=_('Friday'), blank=True, null=True)
    saturday = models.BooleanField(verbose_name=_('Saturday'), blank=True, null=True)
    sunday = models.BooleanField(verbose_name=_('Sunday'), blank=True, null=True)
    
    
    def __str__(self):
        return str(self.user)

class Notification(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_notifications', 
                             on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_('Date'), default=timezone.now)
    music = models.ForeignKey(Media, verbose_name=_('Music'), 
                              related_name='music_notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, verbose_name=_('Message'), 
                                related_name='message_notifications', on_delete=models.CASCADE)
    msg_listen = models.BooleanField(verbose_name=_('Message listened'))
    def __str__(self):
        return str(self.user)
    
class Referral(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_referrals', 
                             on_delete=models.CASCADE)
    referred_user = models.ForeignKey(User, verbose_name=_('Referred User '), related_name='referred_users', 
                             on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_('Date'), default=timezone.now)
    referral_link = models.CharField(max_length=255, verbose_name=_('Referral Link'), blank=True, null=True)
    
    def __str__(self):
        return str(self.user)

class SharedItem(TimeStampedModel):
    from_user = models.ForeignKey(User, verbose_name=_('Shared From'), related_name='from_user_shared_item', 
                             on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, verbose_name=_('Shared To'), related_name='to_user_shared_item', 
                             on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_('Date'), default=timezone.now)
    expiration_date = models.DateTimeField(verbose_name=_('Expiration Date'), default=timezone.now)
    
    def __str__(self):
        return 'Shared from %s to %s ' % (str(self.from_user), str(self.to_user))
    
class Testimony(TimeStampedModel):
    
    class Meta:
        verbose_name_plural = _("Testimonies")
        
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_testimonies', 
                             on_delete=models.SET_NULL, blank=True, null=True)
    user_name = models.CharField(max_length=255, verbose_name=_('User Name'), blank=True, null=True,
                             help_text='Use this field if the user is not an internal user')
    message = models.TextField(verbose_name=_('Message')) 
    
    def __str__(self):
        return str(self.user)

class ThemeSuggestions(TimeStampedModel):
    
    class Meta:
        verbose_name_plural = _("Theme Suggestions")
        
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user_theme_suggestions', 
                            on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(verbose_name=_('Message')) 
    