from django.db import models


class Offer(models.Model):
    title = models.CharField("Название:", max_length=50)
    person_info = models.CharField("ФИО:", max_length=100)
    person_email = models.EmailField("Введите свой Email:", max_length=50)
    full_text = models.TextField("Что выставляете на продажу:")
    date = models.DateTimeField("Дата публикации:")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Торговое предложение"
        verbose_name_plural = "Торговые предложения"
