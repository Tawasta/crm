# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2014- Vizucom Oy (http://www.vizucom.com)
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
    'name': 'CRM Claims extension',
    'category': 'Sales',
    'version': '0.5',
    'author': 'Vizucom Oy',
    'website': 'http://www.vizucom.com',
    'depends': ['crm_claim', 'fetchmail'],

    'description': """
Claims extension
=========================================
* Generates account numbers for all existing claims
* Starts from 10001 by default, can be customized in data XML file
* Keeps track of assigned numbers internally, and gives a new one each time a new claim is created
* Removes settled and rejected claims from (default) tree view
* Extends the claims search to partner names
* Adds message history to sent mails
* Adds a company for claims
* Adds a company-spesific reply-to option for claims
* Adds the first-level child partner claims to partner claims-button
* Adds coloring and bolding for claims depending on their state
* Overwrites the claim tree view to colorize claims with new messages and past deadlines
* Splits the 'Claims' submenu element to 'My claims' and 'All claims' for easier access
* Adds an 'autoreply_sent' helper field for automated actions
* Adds an automatic disclaimer to all reply messages
""",
    'data': [
        'view/claim_menu.xml',
        'view/claim_form_view.xml',
        'view/claim_tree_view.xml',
        'view/claim_reply_view.xml',
        'view/claim_search_view.xml',
        'view/fetchmail_server_form_view.xml',
        'data/claim_number_init.xml',
        'security/claim_security.xml',
        'security/ir.model.access.csv',
    ],
}
