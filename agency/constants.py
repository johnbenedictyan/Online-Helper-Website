# Imports from python

# Imports from django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Imports from other apps

# Imports from within the app

# Utiliy Classes and Functions

# Start of Constants

class AreaChoices(models.TextChoices):
    CENTRAL = 'C', _('Central')
    NORTH = 'N', _('North')
    NORTH_EAST = 'NE', _('North East')
    EAST = 'E', _('East')
    WEST = 'W', _('West')