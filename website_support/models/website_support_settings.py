# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
import requests
from odoo.http import request
import odoo

from odoo import api, fields, models

class WebsiteSupportSettings(models.Model):

    _name = "website.support.settings"
    _inherit = 'res.config.settings'

    def _default_product_purchase(self):
        product = self.env['website.support.settings'].search([], order='id desc', limit=1)
        return product.product_purchase.id

    def _default_partner_purchase(self):
        partner = self.env['website.support.settings'].search([], order='id desc', limit=1)
        return partner.partner_purchase

    def _default_personal_shopping(self):
        personal = self.env['website.support.settings'].search([], order='id desc', limit=1)
        return  personal.personal_shopping

    close_ticket_email_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket')]", string="(OBSOLETE)Close Ticket Email Template")
    change_user_email_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket')]", string="Change User Email Template")
    staff_reply_email_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket.compose')]", string="Staff Reply Email Template")
    email_default_category_id = fields.Many2one('website.support.ticket.categories', string="Email Default Category")
    max_ticket_attachments = fields.Integer(string="Max Ticket Attachments")
    max_ticket_attachment_filesize = fields.Integer(string="Max Ticket Attachment Filesize (KB)")
    allow_user_signup = fields.Boolean(string="Allow User Signup")
    auto_send_survey = fields.Boolean(string="Auto Send Survey")
    auto_create_contact = fields.Boolean(string="Auto Create Contact", help="Auto create contact if one with that email does not exist")
    product_purchase = fields.Many2one('product.product', string="Producto para Compras", default=_default_product_purchase)
    partner_purchase = fields.Many2one('res.partner', string="Proveedor para Compras", default=_default_partner_purchase)
    personal_shopping = fields.Many2one('res.users', string="Personal de Compras", default=_default_personal_shopping)

    #-----Auto Create Contact-----

    @api.multi
    def get_default_auto_create_contact(self, fields):
        return {'auto_create_contact': self.env['ir.values'].get_default('website.support.settings', 'auto_create_contact')}

    @api.multi
    def set_default_auto_create_contact(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'auto_create_contact', record.auto_create_contact)


    #-----Auto Send Survey-----

    @api.multi
    def get_default_auto_send_survey(self, fields):
        return {'auto_send_survey': self.env['ir.values'].get_default('website.support.settings', 'auto_send_survey')}

    @api.multi
    def set_default_auto_send_survey(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'auto_send_survey', record.auto_send_survey)
    
    #-----Allow User Signup-----

    @api.multi
    def get_default_allow_user_signup(self, fields):
        return {'allow_user_signup': self.env['ir.values'].get_default('website.support.settings', 'allow_user_signup')}

    @api.multi
    def set_default_allow_user_signup(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'allow_user_signup', record.allow_user_signup)
    
    #-----Change User Email Template-----

    @api.multi
    def get_default_change_user_email_template_id(self, fields):
        return {'change_user_email_template_id': self.env['ir.values'].get_default('website.support.settings', 'change_user_email_template_id')}

    @api.multi
    def set_default_change_user_email_template_id(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'change_user_email_template_id', record.change_user_email_template_id.id)
    
    #-----Close Ticket Email Template-----

    @api.multi
    def get_default_close_ticket_email_template_id(self, fields):
        return {'close_ticket_email_template_id': self.env['ir.values'].get_default('website.support.settings', 'close_ticket_email_template_id')}

    @api.multi
    def set_default_close_ticket_email_template_id(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'close_ticket_email_template_id', record.close_ticket_email_template_id.id)
            
    #-----Email Default Category-----

    @api.multi
    def get_default_email_default_category_id(self, fields):
        return {'email_default_category_id': self.env['ir.values'].get_default('website.support.settings', 'email_default_category_id')}

    @api.multi
    def set_default_email_default_category_id(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'email_default_category_id', record.email_default_category_id.id)
            
    #-----Staff Reply Email Template-----

    @api.multi
    def get_default_staff_reply_email_template_id(self, fields):
        return {'staff_reply_email_template_id': self.env['ir.values'].get_default('website.support.settings', 'staff_reply_email_template_id')}

    @api.multi
    def set_default_staff_reply_email_template_id(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'staff_reply_email_template_id', record.staff_reply_email_template_id.id)

    #-----Max Ticket Attachments-----

    @api.multi
    def get_default_max_ticket_attachments(self, fields):
        return {'max_ticket_attachments': self.env['ir.values'].get_default('website.support.settings', 'max_ticket_attachments')}

    @api.multi
    def set_default_max_ticket_attachments(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'max_ticket_attachments', record.max_ticket_attachments)

    #-----Max Ticket Attachment Filesize-----

    @api.multi
    def get_default_max_ticket_attachment_filesize(self, fields):
        return {'max_ticket_attachment_filesize': self.env['ir.values'].get_default('website.support.settings', 'max_ticket_attachment_filesize')}

    @api.multi
    def set_default_max_ticket_attachment_filesize(self):
        for record in self:
            self.env['ir.values'].set_default('website.support.settings', 'max_ticket_attachment_filesize', record.max_ticket_attachment_filesize)

    #-----Product Purchase -----

    @api.multi
    def get_default_product_purchase(self, fields):
        return {'product_purchase':self.env['ir.values'].get_default('website.support.settings', 'product_purchase')}
    #
    # @api.multi
    # def set_default_product_purchase(self):
    #     for record in self:
    #         self.env['ir.values'].set_default('website.support.settings', 'product_purchase', record.product_purchase)

    # -----Partner Purchase -----

    #
    # @api.multi
    # def set_default_partner_purchase(self):
    #     for record in self:
    #         self.env['ir.values'].set_default('website.support.settings', 'partner_purchase', record.partner_purchase)
