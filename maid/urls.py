# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app
# from .forms import (
    
# )

## Create Views
# from .views import (
        
# )

## Update Views
# from .views import (
    
# )

## Delete Views
# from .views import (
#  
# )

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            
        ])
    ),
    path(
        'delete/',
        include([

        ])
    ),
    path(
        'update/',
        include([

        ])
    )
]
