from typing import TypeVar

from django.db.models.base import Model
from django.forms.forms import Form

T = TypeVar('T', bound=Model)
_FormT = TypeVar('_FormT', bound=Form)
