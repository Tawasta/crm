# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2015- Oy Tawasta Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'CRM Simplification',
    'category': 'CRM',
    'version': '8.0.0.4.2',
    'author': 'Oy Tawasta Technologies Ltd.',
    'website': 'http://www.tawasta.fi',
    'depends': [
        'crm',
        'sale_crm',
        'crm_address_simplification'
    ],
    'description': '''
CRM Simplification
==================

Simplifies CRM views and pipeline


Features
========
* Adds 'My leads' as a default filter for leads
* Cleans up the customer form
* Cleans up the lead form
* Cleans up the opportunity form
* Unifies lead and opportunity form syntax
''',
    'data': [
        'views/res_partner_form.xml',
        'views/res_partner_form_contact.xml',

        'views/crm_lead_form.xml',
        'views/crm_lead_menu.xml',
        'views/crm_lead_search.xml',

        'views/crm_opportunity_form.xml',
        'views/crm_make_sale_form.xml',

        'views/crm_lead_convert_to_opportunity_form.xml',
    ],
}
