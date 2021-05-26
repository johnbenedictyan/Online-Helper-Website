# Imports from the system

# Imports from django

# Imports from foreign installed apps
from enquiry.forms import GeneralEnquiryForm

# Start of Context Processors

def authority(request):
    authority = None
    authority_groups = [
        'Potential Employers',
        'Agency Owners',
        'Agency Administrators',
        'Agency Managers',
        'Agency Sales Staff'
    ]
    if request.user.is_anonymous != True:
        for authority_name in authority_groups:
            if request.user.groups.filter(
                name = authority_name
            ).exists():
                authority = authority_name

    return {
        'authority': authority
    }
    
def cartcount(request):
    return {
        'cart_count': len(request.session.get('cart',[]))
    }
    
def enquiry_form(request):
    return {
        'enquiry_form': GeneralEnquiryForm()
    }
        
def dashboard_side_nav(request):
    dashboard_side_nav_list = [
        #Agency
        'dashboard_agency_detail',
        'dashboard_agency_update',
        'dashboard_agency_information_update',
        'dashboard_agency_outlet_details_update',
        'dashboard_agency_opening_hours_update',
        
        #Agency Employees
        'dashboard_agency_employee_create',
        'dashboard_agency_employee_update',
        
        #Maid
        'dashboard_maid_information_create',
        'dashboard_maid_information_update',
        'dashboard_maid_languages_and_fhpdr_update',
        'dashboard_maid_experience_update',
        'dashboard_maid_employment_history_update',
        'dashboard_maid_about_fdw_update',
        'dashboard_maid_loan_update',

        #Employers
        'employer_create_route',
        'employer_update_route',
        # 'dashboard_employer_detail',
        'employer_sponsor_create_route',
        'employer_sponsor_update_route',
        'employer_jointapplicant_create_route',
        'employer_jointapplicant_update_route',
        'employer_incomedetails_create_route',
        'employer_incomedetails_update_route,'

        #Cases
        'dashboard_case_detail'
    ]
    return {
        'dashboard_side_nav_list' : dashboard_side_nav_list
    }

def page_bar_url_helper(request):
    EMPLOYER_MINI_NAV_URLS = [
        'employer_create_route',
        'employer_update_route',
        'employer_sponsor_create_route',
        'employer_sponsor_update_route',
        'employer_jointapplicant_create_route',
        'employer_jointapplicant_update_route',
        'employer_incomedetails_create_route',
        'employer_incomedetails_update_route,'
    ]

    return {
        'employer_crud_pagebar_urls': EMPLOYER_MINI_NAV_URLS
    }