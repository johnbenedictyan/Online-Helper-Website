# Imports from the system




from enquiry.forms import GeneralEnquiryForm

# Start of Context Processors


def authority(request):
    authority = None
    authority_groups = [
        'Employers',
        'Agency Owners',
        'Agency Administrators',
        'Agency Managers',
        'Agency Sales Staff',
        'Foreign Domestic Workers'
    ]
    if not request.user.is_anonymous:
        for authority_name in authority_groups:
            if request.user.groups.filter(
                name=authority_name
            ).exists():
                authority = authority_name

    return {
        'authority': authority
    }


def cartcount(request):
    return {
        'cart_count': len(request.session.get('cart', []))
    }


def enquiry_form(request):
    return {
        'enquiry_form': GeneralEnquiryForm()
    }


def dashboard_side_nav(request):
    dashboard_side_nav_list = [
        # Agency
        'dashboard_agency_detail',
        'dashboard_agency_information_update',
        'dashboard_agency_outlet_details_update',
        'dashboard_agency_opening_hours_update',

        # Agency Employees
        'dashboard_agency_employee_create',
        'dashboard_agency_employee_update',

        # Maid
        'dashboard_maid_information_create',
        'dashboard_maid_information_update',
        'dashboard_maid_languages_and_fhpdr_update',
        'dashboard_maid_experience_update',
        'dashboard_maid_employment_history_update',
        'dashboard_maid_about_fdw_update',
        'dashboard_maid_loan_update',

        # Employers
        'employer_create_route',
        'employer_update_route',
        'employer_sponsor_create_route',
        'employer_sponsor_update_route',
        'employer_jointapplicant_create_route',
        'employer_jointapplicant_update_route',
        'employer_incomedetails_create_route',
        'employer_incomedetails_update_route',
        'employer_householddetails_route',

        # Cases
        'dashboard_case_detail',
        'case_create_route',
        'case_update_route',
        'servicefee_create_route',
        'servicefee_update_route',
        'serviceagreement_create_route',
        'serviceagreement_update_route',
        'safetyagreement_create_route',
        'safetyagreement_update_route',
        'maid_inventory_route',
        'docupload_create_route',
        'docupload_update_route',
        'case_status_update_route'
    ]
    return {
        'dashboard_side_nav_list': dashboard_side_nav_list
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
        'employer_incomedetails_update_route',
        'employer_householddetails_route'
    ]
    CASE_MINI_NAV_URLS = [
        'case_create_route',
        'case_update_route',
        'case_detail_route',
        'servicefee_create_route',
        'servicefee_update_route',
        'serviceagreement_create_route',
        'serviceagreement_update_route',
        'safetyagreement_create_route',
        'safetyagreement_update_route',
        'maid_inventory_route',
        'docupload_create_route',
        'docupload_update_route',
        'case_status_update_route'
    ]

    return {
        'employer_crud_pagebar_urls': EMPLOYER_MINI_NAV_URLS,
        'case_crud_pagebar_urls': CASE_MINI_NAV_URLS,
    }


def meta_formatter(request):
    url_name_title_map = {
        'agency_sign_up': 'Agency Sign Up | Online Maid',
        'agency_sign_in': 'Agency Log In |  Online Maid',
        'potential_employer_create': 'User Sign Up | Online Maid',
        'sign_in': 'User Log In | Online Maid',
        # 'agency_sign_up': '',
        'password_reset': 'Reset Password | Online Maid',
        'terms_and_conditions_agency': 'T&C for Agency | Online Maid',
        'terms_and_conditions_user': 'T&C for User | Online Maid',
        'privacy_policy': 'Privacy Policy | Online Maid',
        'home': 'Online Maid | #1 Maid Platform in Singapore ',
        'about_us': 'About US | #1 Maid Platform in Singapore | Online Maid',
        'maid_list': 'Search Maid | #1 Maid Platform in Singapore | Online Maid',
        'agency_list': 'Maid Agency | #1 Maid Platform in Singapore | Online Maid',
        'faq': 'FAQ | #1 Maid Platform in Singapore | Online Maid',
        'view_shortlist': 'Shortlist | #1 Maid Platform in Singapore | Online Maid',
        'enquiry_list': 'Enquiry | #1 Maid Platform in Singapore | Online Maid'
    }

    meta_title = ''
    if request.resolver_match:
        if request.resolver_match.url_name in url_name_title_map.keys():
            meta_title = url_name_title_map[request.resolver_match.url_name]
        else:
            meta_title = url_name_title_map['home']

    return {
        'meta_title': meta_title
    }
