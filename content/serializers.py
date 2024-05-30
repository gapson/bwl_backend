from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from content.models import *
from djoser.serializers import UserSerializer

class ProfileSerializer(serializers.ModelSerializer):
    
    user=serializers.StringRelatedField(read_only=True)
    uid= serializers.CharField(read_only=True)
    default_currency_name = serializers.CharField(source='default_currency.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    class Meta:
        model=Profile
        fields='__all__'
        
class UserAlarmSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserAlarmSettings
        fields='__all__'

class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model=Credit
        fields='__all__'
        
class TransactionSerializer(serializers.ModelSerializer):
    credit = serializers.FloatField(read_only=True)
    type = serializers.CharField(read_only=True, source='get_type')
    reference = serializers.CharField(read_only=True, source='get_reference')
    class Meta:
        model = Transaction
        fields='__all__'
        
    def to_representation(self, instance):
        #override to_representation method to prevent an offer to have multiple prices
        if hasattr(instance, 'user'):
            qs = instance.user.user_credits.all()
            instance.credit = qs.count()>0 and qs[0].balance or None
        return super().to_representation(instance)
        
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields='__all__'

class CurrencySerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=True, read_only=True)
    class Meta:
        model = Currency
        fields='__all__'

class UserSerializer(UserSerializer):
    profile = ProfileSerializer(many=False, required=False)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields+\
            ('last_name', 'first_name', 'profile', )
            
    def update(self, instance, validated_data):
        if 'profile' in validated_data:
            profile_data = validated_data.pop('profile')
            profile = instance.profile
            for key, val in profile_data.items():
                setattr(profile, key, val)
            profile.save()
        return super().update(instance, validated_data)

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    profile = ProfileSerializer(many=False)
    refresh= serializers.CharField(read_only=True)
    access= serializers.CharField(read_only=True)
    user_alarm_settings = UserAlarmSettingsSerializer(many=True, read_only=True)
    credit = serializers.FloatField(read_only=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields+\
            ('last_name', 'first_name', 'profile', 'refresh', 'access', 'user_alarm_settings', 'credit')
    
    def to_representation(self, instance):
        #override to_representation method to prevent an offer to have multiple prices
        if hasattr(instance, 'user_credits'):
            qs = instance.user_credits.all()
            instance.credit = qs.count()>0 and qs[0].balance or None
        return super().to_representation(instance)
    
    def validate(self, attrs):
        profile_data = {}
        if 'profile' in attrs:
            profile_data = attrs.pop('profile')
        attrs = super(UserRegistrationSerializer, self).validate(attrs)
        attrs['profile'] = profile_data
        return attrs
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = super(UserRegistrationSerializer, self).create(validated_data)
        if not hasattr(user, 'profile'):
            profile_data['user'] = user
            Profile.objects.create(**profile_data)
        else:
            profile = user.profile
            for key, val in profile_data.items():
                setattr(profile, key, val)
            profile.save()
        token_cred = {'username':validated_data.get('username', ''),
                      'password':validated_data.get('password', '')}
        serializer = TokenObtainPairSerializer(data=token_cred)

        try:
            serializer.is_valid(raise_exception=True)
            token_data = serializer.validated_data
            user.refresh = token_data.get('refresh', '')
            user.access = token_data.get('access', '')
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return user
        
class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = UserRegistrationSerializer(self.user)

        data['user'] = user.data

        return data
    
class AppSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model=AppSetting
        fields='__all__'
        
class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        exclude=('enable_comments','registration_required','template_name', 'sites')

                
class PriceSerializer(serializers.ModelSerializer):
    #currency_name = serializers.CharField(source='currency.name', read_only=True)
    
    class Meta:
        model=Price
        fields= '__all__'

        
class MediaSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    price = PriceSerializer(many=False, required=False)
    class Meta:
        model=Media
        fields='__all__'
        
    def to_representation(self, instance):
        #override to_representation method to prevent an offer to have multiple prices
        if hasattr(instance, 'prices'):
            instance.price = len(instance.prices)>0 and instance.prices[0] or None
        return super().to_representation(instance)
        
class PlaylistSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    class Meta:
        model=Playlist
        fields='__all__'

class MessageSerializer(serializers.ModelSerializer):
    medias = MediaSerializer(many=True, read_only=True)
    class Meta:
        model=Message
        exclude=('users', )

class OfferBasicSerializer(serializers.ModelSerializer):
    price = PriceSerializer(many=False, read_only=True)
    #price = serializers.FloatField(read_only=True)
    class Meta:
        model=Offer
        exclude=['media', 'message']
        
    def to_representation(self, instance):
        #override to_representation method to prevent an offer to have multiple prices
        if hasattr(instance, 'prices'):
            instance.price = len(instance.prices)>0 and instance.prices[0] or None
        return super().to_representation(instance)
        
class OfferSerializer(OfferBasicSerializer):
    price = PriceSerializer(many=False, read_only=True)
    message = MessageSerializer(many=True, read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    class Meta:
        model=Offer
        fields='__all__'
        
class SubscriptionBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model=Subscription
        exclude=['offer', 'currency']
                
class SubscriptionSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(many=False, read_only=False)
    class Meta:
        model=Subscription
        fields='__all__'
        
class SubscriptionUserSerializer(serializers.Serializer):
    current = SubscriptionSerializer(many=False, read_only=True)
    next = SubscriptionBasicSerializer(many=True, read_only=True)
    
class ThemeSuggestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=ThemeSuggestions
        fields='__all__'
    
        