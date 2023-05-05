from django.db import models

from udemy.apps.core.models import ContentBase


class Category(ContentBase):
    """
    Este modelo representa uma categoria de classificação do curso.
    """

    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return f'Category({self.title})'
