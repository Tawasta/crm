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
    'name': 'Lead to Sale',
    'category': 'CRM',
    'version': '8.0.0.2.1',
    'author': 'Oy Tawasta Technologies Ltd.',
    'website': 'http://www.tawasta.fi',
    'depends': [
        'sale_crm',
        'sale_order_description',
    ],
    'description': '''
Lead to Sale
--------------------------

Adds a relation between lead and sale

''',
    'data': [
        #'view/crm_lead_form.xml',
        'view/sale_order_form.xml',
    ],
}
