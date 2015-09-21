# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2015 - Oy Tawasta Technologies Ltd. (http://www.tawasta.fi)
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
    'name': 'CRM Address Simplification',
    'category': 'CRM',
    'version': '8.0.0.3.3',
    'author': 'Oy Tawasta Technologies Ltd.',
    'website': 'http://www.tawasta.fi',
    'depends': ['crm', 'sale_business_id', 'crm_customer_account_number_gen'],
    'data': [
        'views/res_partner_form.xml',
        'views/res_partner_form_contact.xml',
        # 'views/res_partner_form_affiliate.xml',
        'views/res_partner_form_einvoice.xml',
        'views/res_partner_tree_contact.xml',
        'views/res_partner_tree_affiliate.xml',
        'views/res_partner_tree_einvoice.xml',
        # 'views/res_partner_tree.xml',
        'views/res_partner_menu.xml',
        'views/res_partner_search.xml',
    ],
}
