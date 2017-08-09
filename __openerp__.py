# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Panipat Sms Module",
    "version" : "1.0",
    "author" : "harsh jain",
    "category" : "Generic Modules",
    "summary": "Sms Module",
    "sequence":1,
    "description": """
    SMS Module """,
    "data":['panipat_send_sms.xml',
            'panipat_sms_framework.xml',
            'panipat_data.xml',
            'panipat_crm_lead_view.xml',
            'panipat_order_group.xml',
            'sms_wizard.xml',
            'hr_edit.xml'],
    "depends" : ['base','panipat_handloom'],
    "installable": True,
    "application": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
