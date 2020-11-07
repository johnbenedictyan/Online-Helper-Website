# Imports from python

# Imports from django

# Imports from other apps
from agency.models import Agency, AgencyAdministrator, AgencyEmployee

# Imports from within the app

# Utiliy Classes and Functions

# Start of Mixins
class AgencyOwnerRequiredMixin:
    def check_owner(self):
        if Agency.objects.get(
            pk = self.request.user.pk
        ):
            return self.request.user.pk


    def dispatch(self, request, *args, **kwargs):
        if not self.check_owner():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)

class AdministratorRequiredMixin:
    def check_administrator(self):
        if Agency.objects.get(
            pk = self.request.user.pk
        ) or AgencyAdministrator.objects.get(
            pk = self.request.user.pk
        ):
            return self.request.user.pk


    def dispatch(self, request, *args, **kwargs):
        if not self.check_administrator():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)

class VerifiedAgencyEmployeeMixin:
    def check_employee_role(self):
        role = None
        user_pk = self.request.user.pk
        if Agency.objects.get(
            pk = user_pk
        ):
            role = 'owner'
        elif AgencyAdministrator.objects.get(
            pk = user_pk,
            agency = Agency.objects.get(
                pk = self.pk_url_kwarg
            )
        ):
            role = 'administrator'
        else:
            try:
                employee = AgencyEmployee.objects.get(
                    pk = user_pk,
                    agency = Agency.objects.get(
                        pk = self.pk_url_kwarg
                    )
                )   
            except AgencyEmployee.DoesNotExist:
                pass
            else:
                if employee.role == 'M':
                    role = 'manager'
                elif employee.role == 'S':
                    role = 'sales'

        return role

    def dispatch(self, request, *args, **kwargs):
        if not self.check_employee_role():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'role': self.check_employee_role()
        })
        return context