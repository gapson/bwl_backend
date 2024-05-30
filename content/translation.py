from modeltranslation.translator import translator, TranslationOptions
from django.contrib.flatpages.models import FlatPage

from content.models import Media, Page, Offer

class MediaTranslation(TranslationOptions):
    fields = ('title', 'description', 'url_link', 'internal_link')
translator.register(Media, MediaTranslation)
    
class OfferTranslation(TranslationOptions):
    fields = ('description', )

translator.register(Offer, OfferTranslation)

class FlatPageTranslation(TranslationOptions):
    fields = ('title', 'content')

translator.register(FlatPage, FlatPageTranslation)

class PageTranslation(TranslationOptions):
    #fields = ('title', 'content')
    pass

translator.register(Page, PageTranslation)