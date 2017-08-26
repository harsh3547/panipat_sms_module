# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import requests
import re

class panipat_sms_wizard(models.TransientModel):
	_name="panipat.sms.wizard"

	customer=fields.Many2one(comodel_name="res.partner",string="Customer")
	recipients=fields.Char("Customer Numbers")
	msg=fields.Text("Message")
	balance=fields.Integer("Your Current Balance is:")
	forwardto=fields.Many2many(comodel_name='res.partner',string="Forward Contacts")
	forwardto_numbers=fields.Char("Contact Nos.")
	test_mode=fields.Boolean("Test Mode")
	send_later=fields.Boolean("Send On Later Date")
	later_datetime=fields.Datetime("Later Date")

	
	@api.onchange("customer")
	def onchange_customer(self):
		mobile=self.customer.mobile
		if mobile:
		    self.recipients=str(mobile)
		else:
		    self.recipients="-empty-"

	@api.onchange("forwardto")
	def onchange_partners(self):
		numbers=[]
		for rec in self.forwardto:
		    if rec.mobile:
		        numbers.append(str(rec.mobile))
		    else:
		        numbers.append("-empty-")
		self.forwardto_numbers=",".join(numbers)


	def create_sms_list(self,vals):
	    return self.env['panipat.sms.list'].create(vals)

	@api.multi
	def send_sms(self):
		print "--------context--------",self._context
		rec_framework=self.env['panipat.sms.framework'].search([])
		api_endpoint="http://api.textlocal.in/send/"
		data_sms={'apikey':rec_framework.apikey,'sender':rec_framework.sender_name,'test':self.test_mode}
		final_numbers=[]
		customer_id=self.customer.id
		number_name={}
		
		numbers=str(self.customer.mobile).replace(" ","").split(",")
		#print numbers
		for n in numbers:
			if n:
			    try:
			        int(n)
			    except ValueError:
			        raise except_orm(_('Error!'), _('Each Number of Customer should be 10 digits only'))
			    if len(str(int(n)))!=10:
			        raise except_orm(_('Error!'), _('Each Number of Customer should be 10 digits only'))
			    #print n
			    final_numbers.append(n)
			    number_name[str(int(n))]=customer_id
		

		#print "-=--=-=-=-=-",forward_numbers
		for rec in self.forwardto:
			n1=rec.mobile
			if n1:
			    try:
			        int(n1)
			    except ValueError:
			        raise except_orm(_('Error!'), _('Each forward Number should be 10 digits only. please check the contacts of forward numbers'))
			    if len(str(int(n1)))!=10:
			        raise except_orm(_('Error!'), _('Each forward Number should be 10 digits only. please check the contacts of forward numbers'))
			    #print n
			    final_numbers.append(n1)
			    number_name[str(int(n1))]=rec.id
		
		print "---final numbers---",final_numbers
		data_sms['numbers']=",".join(final_numbers)
		data_sms['message']=self.msg.replace("\n", "%n").replace("%%","")
		
		print data_sms
		print len(data_sms['message'])

		try:
		    resp = requests.post(url=api_endpoint,data=data_sms)
		    response = resp.json()
		    print response
		    if response['status']=='success':
		    	#print "----context----",self._context
		    	rec_framework.getbalance()
		    	vals_sms_list={}
		    	vals_sms_list['cost']=response['cost']
		    	vals_sms_list['content']=response['message']['content'].replace("%n", "\n")
		    	vals_sms_list['sender']=response['message']['sender']
		    	vals_sms_list['total_num']=response['num_messages']
		    	vals_sms_list['num_parts']=response['message']['num_parts']
		    	vals_sms_list['msg_header']=self._context['msg_title']
		    	vals_sms_list['sent_from']=self._context['active_model']+','+str(self._context['active_id'])
		    	vals_sms_list['partner']=customer_id
		    	vals_sms_list['single_ids']=[]
		    	msg_ids=[]
		    	for ids in response['messages']:
		    	    vals_sms_list['single_ids'].append((0,0,{
		    	    	'id_msg':ids['id'],
		    	    	'recipient':ids['recipient'],
		    	    	'partner':number_name.get(str(ids['recipient'])[2:],False),
		    	    	'sent_time':fields.datetime.now(),
		    	    	'status':'?'}))
		    	    msg_ids.append(ids['id'])

		    	print "vals_sms_list-===============",vals_sms_list
		    	if 'test_mode' in response:
		    	    return {
		    	            'type': 'ir.actions.client',
		    	            'tag': 'action_warn',
		    	            'name': 'Success',
		    	            'params': {
		    	                       'title': 'SUCCESS!',
		    	                       'text': 'Your test message can be sent.',
		    	                       }
		    	            }
		    	else:
		    	    rec_sms_list=self.create_sms_list(vals_sms_list)
		    	    return {
		    	            'name': 'Panipat Sms List',
		    	            'view_type': 'form',
		    	            'view_mode': 'form',
		    	            'res_model': 'panipat.sms.list',
		    	            'type': 'ir.actions.act_window',
		    	            'res_id': rec_sms_list.id,
		    	            'context':self._context
		    	            }


		    else:
		        raise except_orm(_('Error!'), _('Please Contact administrator \n %s'%(str(resp.text))))
		except requests.exceptions.RequestException as e:  # This is the correct syntax
		    raise except_orm(_('Error!'), _('Please check internet \n\n Please Contact administrator \n %s'%(e)))


