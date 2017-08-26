# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import requests
import re


class panipat_crm_lead(models.Model):
	_inherit="panipat.crm.lead"

	
	@api.multi
	def employee_msg(self):
		rec_template=self.env['panipat.sms.framework.templates'].search([("title","=","employee_msg")])
		msg=re.sub(r'%%.+%%',"%% "+ company_phone +" %%",rec_template.msg_content)
		numbers=self.partner_id.mobile
		customer=self.partner_id.id
		balance=rec_template.framework_id.credits_left
		forward_ids=rec_template.forwardto.ids
		title=rec_template.title
		return {
                'name': 'Sms Wizard Form',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id':self.env.ref('panipat_sms_module.view_panipat_sms_wizard').id,
                'res_model': 'panipat.sms.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
                'context':{
                	'default_customer':customer,
                	'default_recipients':numbers,
                	'default_msg':msg,
                	'default_balance':balance,
                	'default_forwardto':[(6, 0, forward_ids)],
                	'msg_title':title
                			}
                }


	@api.multi
	def welcome_msg(self):
		rec_template=self.env['panipat.sms.framework.templates'].search([("title","=","thanks visit")])
		company_phone = self.custom_company.phone if self.custom_company.phone else "Enter Company phone no , maxlength = 22"
		msg=re.sub(r'%%.+%%',"%% "+ company_phone +" %%",rec_template.msg_content)
		numbers=self.partner_id.mobile
		customer=self.partner_id.id
		balance=rec_template.framework_id.credits_left
		forward_ids=rec_template.forwardto.ids
		title=rec_template.title
		return {
                'name': 'Sms Wizard Form',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id':self.env.ref('panipat_sms_module.view_panipat_sms_wizard').id,
                'res_model': 'panipat.sms.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
                'context':{
                	'default_customer':customer,
                	'default_recipients':numbers,
                	'default_msg':msg,
                	'default_balance':balance,
                	'default_forwardto':[(6, 0, forward_ids)],
                	'msg_title':title
                			}
                }

	@api.multi
	def measurement_msg(self):
		rec_template=self.env['panipat.sms.framework.templates'].search([("title","=","measurement_rep")])
		msg=re.sub(r'%%.+%%',"%% Enter Date/Day , maxlength = 27 %%",rec_template.msg_content)
		numbers=self.partner_id.mobile
		customer=self.partner_id.id
		balance=rec_template.framework_id.credits_left
		forward_ids=rec_template.forwardto.ids
		employee_time=False
		title=rec_template.title
		for i in self.employee_line:
			if i.start_time:
				d = datetime.strptime(i.start_time, '%Y-%m-%d %H:%M:%S')
				msg=re.sub(r'%%.+%%',d.strftime('%d-%m-%Y'),msg)
				print d.strftime('%d-%m-%Y')
				break
		return {
                'name': 'Sms Wizard Form',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id':self.env.ref('panipat_sms_module.view_panipat_sms_wizard').id,
                'res_model': 'panipat.sms.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
                'context':{
			                'default_customer':customer,
			                'default_recipients':numbers,
			                'default_msg':msg,
			                'default_balance':balance,
			                'default_forwardto':[(6, 0, forward_ids)],
			                'msg_title':title
                			}
                }
		
		
		