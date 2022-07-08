from django.db import models

# Create your models here.


class HomePage(models.Model):
    objects = None
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_show_link = models.BooleanField(default=True)
    slide1 = models.ImageField(upload_to='main/')
    slide2 = models.ImageField(upload_to='main/')
    slide3 = models.ImageField(upload_to='main/')
    content_block = models.ManyToManyField('ContentBlock')
    seo_block = models.ForeignKey('SeoBlock', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.title}'


class ContentBlock(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='main/')

    def __str__(self):
        return f'{self.title}'


class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    title2 = models.CharField(max_length=255)
    description = models.TextField()
    description2 = models.TextField()
    phone = models.ImageField(upload_to='main/')
    gallery = models.ManyToManyField('Gallery', related_name='gallery')
    gallery2 = models.ManyToManyField('Gallery', related_name='gallery2')
    seo_block = models.ForeignKey('SeoBlock', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.title}'


class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='main/files/')
    page = models.ForeignKey('AboutUs', blank=True, null=True, on_delete=models.SET_NULL)


class Contact(models.Model):
    objects = None
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(max_length=125)
    initials = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=125)
    maps = models.TextField()
    seo_block = models.ForeignKey('SeoBlock', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.title}'


class SiteService(models.Model):
    image = models.ImageField(upload_to='main/')
    title = models.CharField(max_length=255)
    description = models.TextField()
    seo_block = models.ForeignKey('SeoBlock', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.title}'


class SeoBlock(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    keywords = models.TextField()

    def __str__(self):
        return f'{self.title}'


class Gallery(models.Model):
    image = models.ImageField(upload_to='main/gallery/')





