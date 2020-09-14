from odoo import api, fields, models

class WebsiteSupportInventory(models.Model):
	_name = 'website.support.inventory'
	_description = "Inventario de Mantenimiento"

	name = fields.Char(string="Producto")
	imagen = fields.Binary(string="Imagen", attachment=True)


