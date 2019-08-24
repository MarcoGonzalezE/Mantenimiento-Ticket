# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools
from HTMLParser import HTMLParser
from random import randint
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
        
class WebsiteSupportTicket(models.Model):

    _name = "website.support.ticket"
    _description = "Solicitud de Mantenimiento"
    _rec_name = "ticket_number_display"
    _inherit = ['mail.thread','ir.needaction_mixin']

    @api.model
    def _read_group_state(self, states, domain, order):
        """ Read group customization in order to display all the states in the
            kanban view, even if they are empty
        """        
        #staff_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_replied')
        #customer_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')
        #customer_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_closed')
        staff_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed')
        
        #exclude_states = [staff_replied_state.id, customer_replied_state.id, customer_closed.id, staff_closed.id]
        exclude_states = [staff_closed.id]
        
        #state_ids = states._search([('id','not in',exclude_states)], order=order, access_rights_uid=SUPERUSER_ID)
        state_ids = states._search([], order=order, access_rights_uid=SUPERUSER_ID)
        
        return states.browse(state_ids)
        
    def _default_state(self):
        return self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_awaiting_approval')

    """def _default_gerencia(self):
        return self.env['res.users'].search([('name','=','Luz Alvarez')]) """
    def _default_fecha(self):
        return datetime.datetime.now()

    
    def _default_priority_id(self):
        default_priority = self.env['website.support.ticket.priority'].search([('sequence','=','1')])
        return default_priority[0]

    def _default_approval_id(self):
        try:
            return self.env['ir.model.data'].get_object('website_support', 'awaiting_approval')
        except ValueError:
            return False



#Campos de Jefe de Granja
    approval_id = fields.Many2one('website.support.ticket.approval', default=_default_approval_id, string="Estado de aprobación", track_visibility='onchange')
        #TODO: Autocompletar este campo al cambiar la categoria
    partner_id = fields.Many2one('res.partner', string="Jefe de Granja", compute="_compute_partner", store=True)
    priority_id = fields.Many2one('website.support.ticket.priority', default=_default_priority_id, string="Prioridad", track_visibility='onchange')
        #TODO: onchage event
    category = fields.Many2one('website.support.ticket.categories', string="Granja", track_visibility='onchange')
    


#Campos de Ticket o Encargado de Granja
    create_user_id = fields.Many2one('res.users', "Creado por")
    fecha_solicitud = fields.Datetime(string="Fecha de Solicitud", default=_default_fecha)
    person_name = fields.Char(string="Solicitante")
    subject = fields.Char(string="Asunto")
    description = fields.Text(string="Descripcion")
    state = fields.Many2one('website.support.ticket.states', default=_default_state, group_expand='_read_group_state', string="Estado", track_visibility='onchange')
    conversation_history = fields.One2many('website.support.ticket.message', 'ticket_id', string="Conversation History")
    attachment = fields.Binary(string="Archivos")
    attachment_filename = fields.Char(string="Archivos Adjuntos")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'website.support.ticket')], string="Adjuntos")
    unattended = fields.Boolean(string="Unattended", compute="_compute_unattend", store="True", help="In 'Open' state or 'Customer Replied' state taken into consideration name changes")
    portal_access_key = fields.Char(string="Portal Access Key")
    ticket_number = fields.Integer(string="Reporte #")
    ticket_number_display = fields.Char(string="Reporte #", compute="_compute_ticket_number_display")
    ticket_color = fields.Char(related="prioridad_mant.color", string="Ticket Color")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env['res.company']._company_default_get('website.support.ticket') )
    support_rating = fields.Integer(string="Calificacion del Servicio")
    support_comment = fields.Text(string="Comentarios")
    close_comment = fields.Text(string="Nota:")
    close_time = fields.Datetime(string="Terminacion Real")
    close_date = fields.Date(string="Close Date")
    closed_by_id = fields.Many2one('res.users', string="Closed By")
    time_to_close = fields.Integer(string="Tiempo de terminacion real (Dias)")
    time_to_close_est = fields.Integer(string="Tiempo de terminacion estimado (Dias)", compute="_compute_tiempo_est")
    extra_field_ids = fields.One2many('website.support.ticket.field', 'wst_id', string="Extra Details")
    approve_url = fields.Char(compute="_compute_approve_url", string="Approve URL")
    disapprove_url = fields.Char(compute="_compute_disapprove_url", string="Disapprove URL")
    fecha_incio_real = fields.Datetime(string="Inicio real")
    current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    compras_ids = fields.One2many('purchase.order', 'reporte', string='Compra(s)')

#Campos de Personal de Mantenimiento
    user_id = fields.Many2one('res.partner', string="Responsable", track_visibility='onchange')
    prioridad_mant = fields.Many2one('website.support.ticket.priority', string="Prioridad de Mantenimiento", track_visibility='onchange')
    asignar = fields.Many2one('personal.mantenimiento', string="Asignado a", track_visibility='onchange')
    cat_mant_id = fields.Many2one('mantenimiento.categoria', string="Categoria", track_visibility='onchange')
    tipo_mant_id = fields.Many2one('mantenimiento.tipo', string="Tipo de Matenimiento", track_visibility='onchange')
    fecha_estimada = fields.Datetime(string="Fecha Estimada", track_visibility='onchange')
    fecha_reporte = fields.Datetime(string="Fecha de Reporte")

#TODO: Futuras Ideas    
    #email_ger = fields.Char(string="Correo de Gerencia")
    email = fields.Char(string="Correo")
    support_email = fields.Char(string="Support Email")
    #sub_category_id = fields.Many2one('mantenimiento.tipo', string="Tipo de Matenimiento")    
    #valor_state = fields.Char(related='state.name')
    


#Indicadores
    group_mant = fields.Boolean(string="Grupo de Mantenimieto", compute="_get_mant")
    group_jefe = fields.Boolean(string="Grupo Jefe de Granja", compute="_get_jefe")
    enviado = fields.Boolean(string="Solicitud enviada a Mantenimiento")
    cancelar = fields.Boolean(string="Cancelacion de solicitud")

    #@Author: Ivan Porras
    @api.multi
    @api.depends('category')
    def _compute_partner(self):
        for r in self:
            categories = self.env['website.support.ticket.categories'].search([('id','=',r.category.id)],limit=1)
            r.partner_id = self.env['res.partner'].search([('id','=',categories.cat_user_ids.partner_id.id)])

    @api.multi
    @api.depends('tipo_mant_id')
    def _compute_mant_person(self):
        for r in self:
            r.user_id = None
            personal=[]
            mant_person = self.env['mantenimiento.tipo'].search([('id','=',r.tipo_mant_id.id)])
            for x in mant_person.mant_user_ids:
                personal.append(int(x.partner_id.id))
            if len(personal)>0:
                return {'domain':{'user_id':[('id','in',personal)]}}
        self.user_id = self.env['res.partner'].search([('id','=',mant_person.mant_user_ids.partner_id.id)])

    # @api.depends('state')
    # def _compute_is_state(self):
    #     for x in self:
    #         x.is_state = (x.state.name == self.env.ref("website.support.ticket.states").name)
#Para identificar grupo en que pertenece el usuario logeado
    #JEFE DE GRANJA
    @api.depends('group_jefe')
    def _get_jefe(self):
        user_crnt = self._uid
        res_user = self.env['res.users'].search([('id','=',self._uid)]) 
        if res_user.has_group('website_support.support_staff'):
            self.group_jefe = True
        else:
            self.group_jefe = False
    #PERSONAL DE MANTENIMIENTO
    @api.depends('group_mant')
    def _get_mant(self):
        user_crnt = self._uid
        res_user = self.env['res.users'].search([('id','=',self._uid)]) 
        if res_user.has_group('website_support.support_mant'): 
            self.group_mant = True
        else:
            self.group_mant = False

    @api.multi
    @api.depends('fecha_estimada')
    def _compute_tiempo_est(self):
        if self.fecha_estimada != False:
            d1= datetime.datetime.strptime(str(self.fecha_estimada), DEFAULT_SERVER_DATETIME_FORMAT)
            d2= datetime.datetime.strptime(str(self.fecha_reporte), DEFAULT_SERVER_DATETIME_FORMAT)
            diff_time_est = abs((d1-d2))
        #diff_time_est = datetime.datetime.strptime(self.fecha_estimada, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.fecha_incio_real, DEFAULT_SERVER_DATETIME_FORMAT)
        #diff_time_est= datetime.datetime.strptime(self.fecha_estimada, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.fecha_incio_real, DEFAULT_SERVER_DATETIME_FORMAT)
            self.time_to_close_est = diff_time_est.days

    #NUEVO
    @api.onchange('approval_id')
    def _compute_state(self):
        if self.approval_id.name == 'Rechazado':
            self.state = self.env['website.support.ticket.states'].search([('name','=','Rechazado')])
        if self.approval_id.name == 'Aceptado':
            self.state = self.env['website.support.ticket.states'].search([('name','=','Aceptado')])
    @api.one
    def _compute_approve_url(self):
        self.approve_url = "/support/approve/" + str(self.id)

    @api.one
    def _compute_disapprove_url(self):
        self.disapprove_url = "/support/disapprove/" + str(self.id)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):      
        #self.person_name = self.partner_id.name
        self.email = self.partner_id.email

    @api.onchange('asignar')
    def _inicio_real(self):                   
        self.fecha_incio_real = datetime.datetime.now()
        self.state = self.env['website.support.ticket.states'].search([('name','=','En Proceso')])

    @api.multi
    @api.depends('compras_ids')
    def _compras_state(self):
        compras=[]
        for x in self.compras_ids:
            compras.append(x.state)
        if 'purchase' in compras:
            self.state = self.env['website.support.ticket.states'].search([('name','=','Autorizado por Gerencia')]) 
        else:
            self.state= self.env['website.support.ticket.states'].search([('name','=','Esperando material')])


    def message_new(self, msg, custom_values=None):
        """ Create new support ticket upon receiving new email"""

        defaults = {'support_email': msg.get('to'), 'subject': msg.get('subject')}

        #Extract the name from the from email if you can        
        if "<" in msg.get('from') and ">" in msg.get('from'):
            start = msg.get('from').rindex( "<" ) + 1
            end = msg.get('from').rindex( ">", start )
            from_email = msg.get('from')[start:end]
            from_name = msg.get('from').split("<")[0].strip()
            defaults['person_name'] = from_name
        else:
            from_email = msg.get('from')

        defaults['email'] = from_email
        
        #Try to find the partner using the from email
        search_partner = self.env['res.partner'].sudo().search([('email','=', from_email)])
        if len(search_partner) > 0:
            defaults['partner_id'] = search_partner[0].id
            defaults['person_name'] = search_partner[0].name

        defaults['description'] = tools.html_sanitize(msg.get('body'))
        
        portal_access_key = randint(1000000000,2000000000)
        defaults['portal_access_key'] = portal_access_key

        #Assign to default category
        setting_email_default_category_id = self.env['ir.values'].get_default('website.support.settings', 'email_default_category_id')
        
        if setting_email_default_category_id:
            defaults['category'] = setting_email_default_category_id
        
        return super(WebsiteSupportTicket, self).message_new(msg, custom_values=defaults)

    def message_update(self, msg_dict, update_vals=None):
        """ Override to update the support ticket according to the email. """

        body_short = tools.html_sanitize(msg_dict['body'])
        #body_short = tools.html_email_clean(msg_dict['body'], shorten=True, remove=True)
                
        #s = MLStripper()
        #s.feed(body_short)
        #body_short = s.get_data()
                
        #Add to message history field for back compatablity
        self.conversation_history.create({'ticket_id': self.id, 'by': 'customer', 'content': body_short })

        #If the to email address is to the customer then it must be a staff member...
        #if msg_dict.get('to') == self.email:
        #    change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')        
        #else:
        #    change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_customer_replied')
        
        #self.state = change_state.id

        return super(WebsiteSupportTicket, self).message_update(msg_dict, update_vals=update_vals)

    @api.one
    @api.depends('ticket_number')
    def _compute_ticket_number_display(self):
        self.ticket_number_display = 'RM' + str(self.ticket_number)

        #if self.ticket_number:
        #    self.ticket_number_display = str(self.id) + " / " + "{:,}".format( self.ticket_number ) #Por Borrar
        #else:
        #    self.ticket_number_display = self.id
            
    @api.depends('state')
    def _compute_unattend(self):
        #staff_replied = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_replied')
        #customer_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_closed')
        staff_closed = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed')
        cancelled = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_cancelled')
        approval_rejected = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_approval_rejected')

        #If not closed or replied to then consider all other states to be attended to
        #if self.state != staff_replied and self.state != customer_closed and self.state != staff_closed:
        if self.state != staff_closed and self.state != cancelled and self.state != approval_rejected:
            self.unattended = True

    #working on it
    @api.multi
    def request_approval(self):

        request_message = "Se requiere la aprobacion antes de que podamos continuar con esta solicitud<br/>"
        request_message += '<a href="' + self.approve_url + '">APROBAR</a><br/>'
        request_message += '<a href="' + self.disapprove_url + '"' + ">NO APROBAR</a><br/>"
        self.email = self.partner_id.email
        return {
            'name': "Pedir aprobación",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.compose',
            'context': {'default_ticket_id': self.id, 'default_email': self.email, 'default_subject': self.subject, 'default_approval': True, 'default_body': request_message},
            'target': 'new'
        }
        
    @api.multi
    def open_close_ticket_wizard(self):
        if self.state.name == 'Rechazado':
            raise ValidationError('NO SE PUEDE TERMINAR UNA SOLICITUD RECHAZADA')
        elif self.user_id == False:
            raise ValidationError('NO SE PUEDE TERMINAR UNA SOLICITUD SIN RESPONSABLE ASIGNADO')
        else:
            return {
                'name': "Close Support Ticket",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'website.support.ticket.close',
                'context': {'default_ticket_id': self.id},
                'target': 'new'
            }

    ''' Funcion eliminada por borrar el status "Cliente Respondio" @ivan.porras
    @api.model
    def _needaction_domain_get(self):
        open_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        custom_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')
        return ['|',('state', '=', open_state.id ), ('state', '=', custom_replied_state.id)]
    '''
    @api.model
    def create(self, vals):


        new_id = super(WebsiteSupportTicket, self).create(vals)

        new_id.ticket_number = new_id.company_id.next_support_ticket_number

        #Add one to the next ticket number
        new_id.company_id.next_support_ticket_number += 1

        #Auto create contact if one with that email does not exist
        setting_auto_create_contact = self.env['ir.values'].get_default('website.support.settings', 'auto_create_contact')
        new_id.fecha_reporte = datetime.datetime.now()
        new_id.fecha_solicitud = datetime.datetime.now()

        if setting_auto_create_contact and 'email' in vals:
            if self.env['res.partner'].search_count([('email','=',vals['email'])]) == 0:
                if 'person_name' in vals:
                    new_contact = self.env['res.partner'].create({'name':vals['person_name'], 'email': vals['email'], 'company_type': 'person'})
                else:
                    new_contact = self.env['res.partner'].create({'name':vals['email'], 'email': vals['email'], 'company_type': 'person'})
                    
                new_id.partner_id = new_contact.id
                    
        #(BACK COMPATABILITY) Fail safe if no template is selected, future versions will allow disabling email by removing template
        #ticket_open_email_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open').mail_template_id
        #if ticket_open_email_template == False:
        #    ticket_open_email_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_new')
        #    ticket_open_email_template.send_mail(new_id.id, True)
        #else:
        #    ticket_open_email_template.send_mail(new_id.id, True)

        #Send an email out to everyone in the category
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category')
        support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_menu')
        support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_action')
        
        for my_user in new_id.category.cat_user_ids:
            values = notification_template.generate_email(new_id.id)
            values['body_html'] = values['body_html'].replace("_ticket_url_", "web#id=" + str(new_id.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  my_user.partner_id.name)
            #values['body'] = values['body_html']
            values['email_to'] = my_user.partner_id.email                        
            send_mail = self.env['mail.mail'].create(values)
            send_mail.send()            
            #Remove the message from the chatter since this would bloat the communication history by a lot
            send_mail.mail_message_id.res_id = 0

        return new_id
        
    @api.multi
    def write(self, values):
        for r in self:
            if 'state' in values:
                if r.state.mail_template_id:
                    r.state.mail_template_id.send_mail(r.id, True)
        #Email user if category has changed
        # if 'category' in values:
        #     change_category_email = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category_change')
        #     change_category_email.send_mail(self.id, True)
            if 'user_id' in values:
                setting_change_user_email_template_id = self.env['ir.values'].get_default('website.support.settings', 'change_user_email_template_id')
                if setting_change_user_email_template_id:
                    email_template = self.env['mail.template'].browse(setting_change_user_email_template_id)
                else:
                    #Default email template
                    email_template = self.env['ir.model.data'].get_object('website_support','support_ticket_user_change')
                email_values = email_template.generate_email([r.id])[r.id]
                email_values['model'] = "website.support.ticket"
                email_values['res_id'] = r.id
                print(values['user_id'])
                assigned_user = self.env['res.partner'].browse(int(values['user_id']))
                email_values['email_to'] = assigned_user.email
                email_values['body_html'] = email_values['body_html'].replace("_user_name_", assigned_user.name)
                email_values['body'] = email_values['body'].replace("_user_name_", assigned_user.name)
                send_mail = self.env['mail.mail'].create(email_values)
                send_mail.send()
            update_rec = super(WebsiteSupportTicket, r).write(values)
            return update_rec

    def send_survey(self):
        if self.state.name != 'Terminado':
            raise ValidationError('No se puede enviar la evaluacion sin TERMINAR el reporte.')
        else:
            notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_survey')
            values = notification_template.generate_email(self.id)
            surevey_url = "support/survey/" + str(self.portal_access_key)
            values['body_html'] = values['body_html'].replace("_survey_url_",surevey_url)
            values['email_to'] = self.partner_id.email
            send_mail = self.env['mail.mail'].create(values)
            send_mail.send(True)

   
    def send_mantenimiento(self):        
        support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_menu')
        support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_action')
        for my_user in self.tipo_mant_id.mant_user_ids:
            notification_mant = self.env['ir.model.data'].sudo().get_object('website_support', 'mantenimiento_support')
            email_values = notification_mant.generate_email(self.id)
            email_values['model'] = "website.support.ticket"
            email_values['res_id'] = self.id            
            email_values['email_to'] = my_user.partner_id.email
            email_values['body_html'] = email_values['body_html'].replace("_ticket_url_", "web#id=" + str(self.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  my_user.partner_id.name)
            email_values['body'] = email_values['body'].replace("_user_name_", my_user.partner_id.name)
            send_mail = self.env['mail.mail'].create(email_values)
            send_mail.send()
        if self.tipo_mant_id.mant_user_ids == False:
            raise ValidationError('Personal de Mantenimiento no esta asignada al tipo de Mantenimiento')
        else:
            self.enviado = True

    def solicitud_cancelar(self):
        self.state = self.env['website.support.ticket.states'].search([('name','=','Cancelado')])
        self.cancelar = True

class WebsiteSupportTicketApproval(models.Model):

    _name = "website.support.ticket.approval"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Name", translate=True)

class WebsiteSupportTicketField(models.Model):

    _name = "website.support.ticket.field"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Label")
    value = fields.Char(string="Value")
    
class WebsiteSupportTicketMessage(models.Model):

    _name = "website.support.ticket.message"
    
    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    by = fields.Selection([('staff','Staff'), ('customer','Customer')], string="By")
    content = fields.Html(string="Content")
   
class WebsiteSupportTicketCategories(models.Model):

    _name = "website.support.ticket.categories"
    _order = "sequence asc"
    
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Granja')
    cat_user_ids = fields.Many2many('res.users', string="Jefe de Granja")
    encargados_ids = fields.Many2many('res.partner', string="Encargados de Granja")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.categories')
        values['sequence']=sequence
        return super(WebsiteSupportTicketCategories, self).create(values)

        
class WebsiteSupportTicketSubCategories(models.Model):

    _name = "website.support.ticket.subcategory"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Tipo de Matenimiento')   
    #parent_category_id = fields.Many2one('website.support.ticket.categories', required=True, string="Parent Category")
    additional_field_ids = fields.One2many('website.support.ticket.subcategory.field', 'wsts_id', string="Adicional")
 
    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.subcategory')
        values['sequence']=sequence
        return super(WebsiteSupportTicketSubCategories, self).create(values)

class WebsiteSupportTicketSubCategoryField(models.Model):

    _name = "website.support.ticket.subcategory.field"
        
    wsts_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Category")
    name = fields.Char(string="Etiqueta")
    type = fields.Selection([('textbox','Texto'), ('polar','Si / No')], default="textbox", string="Tipo")
    
class WebsiteSupportTicketStates(models.Model):

    _name = "website.support.ticket.states"
    
    name = fields.Char(required=True, translate=True, string='State Name')
    mail_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket')]", string="Mail Template")

class WebsiteSupportTicketPriority(models.Model):

    _name = "website.support.ticket.priority"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string="Priority Name")
    color = fields.Char(string="Color")
    
    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.priority')
        values['sequence']=sequence
        return super(WebsiteSupportTicketPriority, self).create(values)
        
class WebsiteSupportTicketUsers(models.Model):

    _inherit = "res.users"
    
    cat_user_ids = fields.Many2many('website.support.ticket.categories', string="Jefe de Granjas")

class WebsiteSupportTicketEncargados(models.Model):
    _inherit = "res.partner"

    encargados_ids = fields.Many2many('website.support.ticket.categories', string="Encargado")

class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.close"

    ticket_id = fields.Many2one('website.support.ticket', string="Ticket ID")
    message = fields.Text(string="Notas:")

    def close_ticket(self):

        self.ticket_id.close_time = datetime.datetime.now()
        
        #Also set the date for gamification
        self.ticket_id.close_date = datetime.date.today()
        
        diff_time = datetime.datetime.strptime(self.ticket_id.close_time, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.ticket_id.create_date, DEFAULT_SERVER_DATETIME_FORMAT)            
        self.ticket_id.time_to_close = diff_time.days

        

        closed_state = self.env['ir.model.data'].sudo().get_object('website_support', 'website_ticket_state_staff_closed')        
        
        #We record state change manually since it would spam the chatter if every 'Staff Replied' and 'Customer Replied' gets recorded
            #message = "<ul class=\"o_mail_thread_message_tracking\">\n<li>State:<span> " + self.ticket_id.state.name + " </span><b>-></b> " + closed_state.name + " </span></li></ul>"
            #self.ticket_id.message_post(body=message, subject="Ticket Closed by Staff")

        self.ticket_id.close_comment = self.message
        self.ticket_id.closed_by_id = self.env.user.id
        self.ticket_id.state = closed_state.id

        #Auto send out survey
            #setting_auto_send_survey = self.env['ir.values'].get_default('website.support.settings', 'auto_send_survey')
            #if setting_auto_send_survey:
                #self.ticket_id.send_survey()
        
        #(BACK COMPATABILITY) Fail safe if no template is selected
            #closed_state_mail_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed').mail_template_id

            #if closed_state_mail_template == False:
            #    closed_state_mail_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_closed')
            #    closed_state_mail_template.send_mail(self.ticket_id.id, True)

    
#working on it
class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.compose"

    ticket_id = fields.Many2one('website.support.ticket', string='Reporte')
    approval = fields.Boolean(string="Approval")
    partner_id = fields.Many2one('res.partner', string="Partner", readonly="True")
    email = fields.Char(string="Email", readonly="True")
    warehouse = fields.Many2one('website.support.warehouse', string="Granja")
    subject = fields.Char(string="Asunto", readonly="True")
    body = fields.Text(string="Message Body")
    template_id = fields.Many2one('mail.template', string="Mail Template", domain="[('model_id','=','website.support.ticket'), ('built_in','=',False)]")
    planned_time = fields.Datetime(string="Planned Time")
    
    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            values = self.env['mail.compose.message'].generate_email_for_composer(self.template_id.id, [self.ticket_id.id])[self.ticket_id.id]                
            self.body = values['body']
            
    @api.one
    def send_reply(self):
        #Send email
        values = {}

        setting_staff_reply_email_template_id = self.env['ir.values'].get_default('website.support.settings', 'staff_reply_email_template_id')
        
        if setting_staff_reply_email_template_id:
            email_wrapper = self.env['mail.template'].browse(setting_staff_reply_email_template_id)
        else:
            #Defaults to staff reply template for back compatablity
            email_wrapper = self.env['ir.model.data'].get_object('website_support','support_ticket_reply_wrapper')

        values = email_wrapper.generate_email([self.id])[self.id]
        values['model'] = "website.support.ticket"
        values['res_id'] = self.ticket_id.id
        send_mail = self.env['mail.mail'].create(values)
        send_mail.send()
        
        #Add to message history field for back compatablity
        self.env['website.support.ticket.message'].create({'ticket_id': self.ticket_id.id, 'by': 'staff', 'content':self.body.replace("<p>","").replace("</p>","")})
        
        #Post in message history
        #self.ticket_id.message_post(body=self.body, subject=self.subject, message_type='comment', subtype='mt_comment')
	
        if self.approval:
	    #Change the ticket state to awaiting approval
	    awaiting_approval_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_awaiting_approval')
	    self.ticket_id.state = awaiting_approval_state.id
	
	    #Also change the approval
	    awaiting_approval = self.env['ir.model.data'].get_object('website_support','awaiting_approval')
	    self.ticket_id.approval_id = awaiting_approval.id        
        #else:
	    #Change the ticket state to staff replied        
	    #staff_replied = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
	    #self.ticket_id.state = staff_replied.id

class WebsiteSupportWarehouse(models.Model):

    _name="website.support.warehouse"

    warehouse = fields.Char(requiered=True, string="Granja")
    sequence = fields.Integer(string="Sequence")
    
    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.warehouse')
        values['sequence']=sequence
        return super(WebsiteSupportWarehouse, self).create(values)


# TIPO DE MANTENIMIENTO
class MantenimientoTipo(models.Model):

    _name = "mantenimiento.tipo"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Tipo de Matenimiento')
    mant_user_ids = fields.Many2many('res.users', string="Jefe de Mantenimiento")
    #parent_category_id = fields.Many2one('mantenimiento.tipo', required=True, string="Parent Category")
    additional_field_ids = fields.One2many('mantenimiento.tipo.etiquetas', 'wsts_id', string="Adicional")
 
    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('mantenimiento.tipo')
        values['sequence']=sequence
        return super(MantenimientoTipo, self).create(values)

class MantenimientoTipoUsers(models.Model):

    _name = "mantenimiento.tipo.users"

    _inherit = "res.users"
    
    mant_user_ids = fields.Many2many('website.support.ticket.categories', string="Personal")


class MantenimientoTipoEtiquetas(models.Model):

    _name = "mantenimiento.tipo.etiquetas"
        
    wsts_id = fields.Many2one('mantenimiento.tipo', string="Tipo de Mantenimiento")
    name = fields.Char(string="Etiqueta")
    type = fields.Selection([('textbox','Texto'), ('polar','Si / No')], default="textbox", string="Tipo")

#PERSONAL DE MANTENIMIENTO
class PersonalMantenimiento(models.Model):
    _name = "personal.mantenimiento"

    name = fields.Char(string="Nombre")
        

#CATEGORIA DE MANTENIMIENTO
class MantenimientoCategoria(models.Model):

    _name = "mantenimiento.categoria"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True, string='Categoria Matenimiento')

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('mantenimiento.categoria')
        values['sequence']=sequence
        return super(MantenimientoCategoria, self).create(values)

#PEDIDO DE COMPRA
class orden_servicio(models.Model):
    _inherit = "purchase.order"
    reporte = fields.Many2one('website.support.ticket',  string='Reporte de Mantenimiento')

class AcercaDe(models.Model):
    _name = "acerca.de"

    name = fields.Binary('Description')