from django.db import models


class MainPage(models.Model):

    """Главная страница"""
    photo = models.ImageField("Выберите фотографию: ", upload_to="mainapp/", null=True, blank=True)
    name = models.CharField(verbose_name="Название: ", max_length=50)
    description = models.CharField(verbose_name="Описание в админке: ", max_length=50)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL перехода: ", db_index=True)

    def __str__(self):
        return "{}".format(self.description)

    class Meta:
        verbose_name = "Оформление главной страницы страниц"
        verbose_name_plural = "Оформление главной страницы страниц"
