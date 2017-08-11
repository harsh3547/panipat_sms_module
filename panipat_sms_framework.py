# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import requests
import re
import pytz
import logging
import time

_logger = logging.getLogger(__name__)


class panipat_sms_framework(models.Model):
    _name = "panipat.sms.framework"
    _rec_name="sender_name"
    
    apikey=fields.Char(string="Api Key")
    credits_left=fields.Integer(string="Balance Left")
    sender_name=fields.Char(string="Sender Names")
    templates=fields.One2many(comodel_name='panipat.sms.framework.templates', inverse_name="framework_id", string="Pre-Approved Messages")

    '''
    @api.model
    def create(self,vals):
        ids=self.search([])
        if ids and len(ids)>=1:
            raise except_orm(_('Error!'), _('Cannot create more than one settings for sms'))
        return super(panipat_sms_framework, self).create(vals)
    '''

    @api.multi
    def getbalance(self):
        #print "------------------------090909090909090",self._context
        api_endpoint= "http://api.textlocal.in/balance/"
        api_key=self.apikey
        data={'apiKey':api_key}
        try:
            resp = requests.post(url=api_endpoint,data=data)
            j = resp.json()
            print resp.text
            print j['status']
            if j['status']=='success':
                self.credits_left=j['balance']['sms']
            elif "params" not in self._context:
                pass
            else:
                raise except_orm(_('Error!'), _('Please Contact administrator \n %s'%(str(resp.text))))    
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            if "params" not in self._context:
                pass # This is to not raise error if function run on install of module
            else:
                raise except_orm(_('Error!'), _('Please check internet \nPlease Contact administrator \n %s'%(e)))

    @api.multi
    def get_sender_names(self):
        api_endpoint= "http://api.textlocal.in/get_sender_names/"
        api_key=self.apikey
        data={'apiKey':api_key}
        try:
            resp = requests.post(url=api_endpoint,data=data)
            j = resp.json()
            print resp.text
            print j['status']
            if j['status']=='success':
                self.sender_name=j['default_sender_name']
            elif "params" not in self._context:
                pass
            else:
                raise except_orm(_('Error!'), _('Please Contact administrator \n %s'%(str(resp.text))))    
        except requests.exceptions.RequestException as e:  # This is to not raise error if function run on install of module
            if "params" not in self._context:
                pass
            else:
                raise except_orm(_('Error!'), _('Please check internet \nPlease Contact administrator \n %s'%(e)))


    @api.multi
    def get_templates(self):
        api_endpoint= "http://api.textlocal.in/get_templates/"
        api_key=self.apikey
        data={'apiKey':api_key}
        try:
            resp = requests.post(url=api_endpoint,data=data)
            j = resp.json()
            print resp.text
            print j['status']
            if j['status']=='success':
                existing_template_ids=self.env['panipat.sms.framework.templates'].search([])
                if existing_template_ids:
                    # next few lines to retain existing forwardto and forwardto_employees when templates is downloaded from api
                    title_forwardto={}
                    title_forwardto_employees={}
                    for rec in existing_template_ids:
                        title_forwardto[rec.title]=rec.forwardto
                        title_forwardto_employees[rec.title]=rec.forwardto_employees
                    existing_template_ids.unlink()

                for temp in j['templates']:
                    vals={}
                    vals['title']=temp['title']
                    vals['msg_content']=temp['body']
                    vals['framework_id']=self.id
                    vals['internal_id']=temp['id']
                    vals['senderName']=temp['senderName']
                    vals['dnd']=temp['isMyDND']
                    rec_temp_id=self.env['panipat.sms.framework.templates'].create(vals)

                    forward_ids=map(int,title_forwardto.get(temp['title'],False) or [] )
                    forward_employees_ids=map(int,title_forwardto_employees.get(temp['title'],False) or [] )
                    rec_temp_id.write({'forwardto':[(6,0,forward_ids)],'forwardto_employees':[(6,0,forward_employees_ids)]})

            elif "params" not in self._context:
                pass # This is to not raise error if function run on install of module
            else:
                raise except_orm(_('Error!'), _('Please check internet \nPlease Contact administrator \n %s'%(str(resp.text))))    
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            if "params" not in self._context:
                pass
            else:
                raise except_orm(_('Error!'), _('Please check internet \nPlease Contact administrator \n %s'%(e)))

    def get_message_status(self,id):
        # return status and deliverytime
        # id = id of msg from send_sms api response
        api_status="http://api.textlocal.in/status_message/"
        rec_framework=self.env['panipat.sms.framework'].search([])
        data_status={'apikey':rec_framework.apikey,'message_id':id}
        try:
            resp = requests.post(url=api_status,data=data_status)
            response = resp.json()
            print response
            #print j['status']
            if response['status']=='success':
                return {'status':response['message']['status']}
            else:
                raise except_orm(_('Error!'), _('Please Contact administrator \n %s'%(str(resp.text))))
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise except_orm(_('Error!'), _('Please check internet \n\n Please Contact administrator \n %s'%(e)))

    def indian_to_utc(self,datetime_india):
        # time from api of textlocal is of indian timezone
        # so converting to UTC coz odoo will convert to user's timezone
        tz_name = pytz.timezone("Asia/Kolkata")
        d_tz=tz_name.normalize(tz_name.localize(datetime_india,is_dst=False))
        utc=pytz.timezone("UTC")
        d_utc=d_tz.astimezone(utc)
        print "D_UTC====",d_utc,type(d_utc)
        return d_utc
        

    def utc_to_indian(self,datetime_utc):
        tz_name = pytz.timezone("UTC")
        d_tz=tz_name.normalize(tz_name.localize(datetime_utc,is_dst=False))
        indian_tz=pytz.timezone("Asia/Kolkata")
        d_india=d_tz.astimezone(indian_tz)
        print "d_india===",d_india
        return d_india


class panipat_sms_framework(models.Model):
    _name = "panipat.sms.framework.templates"
    _rec_name="title"

    title=fields.Char(string="Internal Title")
    msg_content=fields.Text(string="Message Content")
    internal_id=fields.Integer(string="id")
    senderName=fields.Char(string="senderName")
    dnd=fields.Char(string="isMyDND")
    framework_id=fields.Many2one(comodel_name='panipat.sms.framework',string="framework",required=True)
    forwardto=fields.Many2many(comodel_name='res.partner',string="Forward To Contacts")
    forwardto_employees=fields.Many2many(comodel_name='hr.employee',string="Forward To Employees")

class panipat_sms_send(models.TransientModel):
    _name="panipat.sms.send"

    partners=fields.Many2many(comodel_name='res.partner',string="Contacts")
    partner_numbers=fields.Char("Contact Nos.")
    recipients=fields.Text("Other Recipients")
    templates=fields.Many2one(comodel_name="panipat.sms.framework.templates",string="Approved Messages")
    msg=fields.Text("Message")
    test_mode=fields.Boolean("Test Mode")
    employee=fields.Many2many(comodel_name='hr.employee',string="Employees")
    employee_numbers=fields.Char("Employee Numbers")


    @api.onchange("partners")
    def onchange_partners(self):
        partner_numbers=[]
        for rec in self.partners:
            if rec.mobile:
                try:
                    int(rec.mobile)
                except ValueError:
                    raise except_orm(_('Error!'), _('Each Contact Number should be 10 digits only. please check the contact ""%s""'%(rec.name)))
                if len(str(int(rec.mobile)))!=10:
                    raise except_orm(_('Error!'), _('Each Contact Number should be 10 digits only. please check the contact ""%s""'%(rec.name)))
                #print n
                partner_numbers.append(str(rec.mobile))
            else:
                partner_numbers.append("-empty-")
        self.partner_numbers=",".join(partner_numbers)

    @api.onchange("employee")
    def onchange_employee(self):
        employee_numbers=[]
        for rec in self.employee:
            if rec.work_phone:
                try:
                    int(rec.work_phone)
                except ValueError:
                    raise except_orm(_('Error!'), _('Each Employee Work Mobile should be 10 digits only. please check the contact ""%s""'%(rec.name)))
                if len(str(int(rec.work_phone)))!=10:
                    raise except_orm(_('Error!'), _('Each Employee Work Mobile should be 10 digits only. please check the contact ""%s""'%(rec.name)))
                #print n
                employee_numbers.append(str(rec.work_phone))
            else:
                employee_numbers.append("-empty-")
        self.employee_numbers=",".join(employee_numbers)


    @api.onchange("templates")
    def onchange_templates(self):
        rec=self.templates
        print "=-========================",type(rec.msg_content)
        if type(rec.msg_content)==type(u'abc'):
            if rec.title=='measurement_rep':
                self.msg=re.sub(r'%%.+%%',"%% Enter Date/Day , maxlength = 27 %%",rec.msg_content)
            elif rec.title=='thanks visit':
                company_phone = self.env.user.company_id.phone if self.env.user.company_id.phone else "Enter Company phone no , maxlength = 22"
                self.msg=re.sub(r'%%.+%%',"%% "+ company_phone +" %%",rec.msg_content)
            elif rec.title=='employee_msg':
                msg=rec.msg_content
                msg=re.sub(r'%%.+employee.+%%',"%% Enter employee name (date for visit)  , maxlength = 100 %%",msg)
                msg=re.sub(r'%%.+number.+%%',"%% Enter contact name and number  , maxlength = 100 %%",msg)
                msg=re.sub(r'%%.+group.+%%',"%% Enter Order Group , maxlength = 8 %%",msg)
                msg=re.sub(r'%%.+lead.+%%',"%% Enter Lead ID , maxlength = 7 %%",msg)
                self.msg=msg
            
