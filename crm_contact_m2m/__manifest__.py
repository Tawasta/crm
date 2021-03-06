##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2015 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

{
    'name': 'CRM Contact M2M',
    'summary': 'Allow contacts to belong to multiple companies',
    'version': '8.0.0.2.3',
    'category': 'CRM',
    'website': 'https://github.com/Tawasta/crm',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'application': False,
    'installable': False,
    'depends': [
        'crm',
        'crm_address_simplification',
    ],
    'data': [
        'views/res_partner_form.xml',
        'views/res_partner_tree.xml',
    ],
}
