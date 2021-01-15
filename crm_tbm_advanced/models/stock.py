from odoo import api, fields, models, _
from odoo.exceptions import UserError
import itertools


class StockMove(models.Model):
    _inherit = 'stock.move'

    #@api.multi
    #@api.depends('move_ids_without_package')
    #def _compute_max_line_sequence(self):
    #    raise UserError(self.move_ids_without_package)
    #    sections = self.env['sale.order.line'].search([
    #        ('order_id', '=', self.sale_id), ('display_type', '=', 'line_section')])
    #    for move in self.move_ids_without_package:
    #        section = sections.filtered(lambda s: move.sale_line_id.sequence > s.sequence)[-1]
    #        raise UserError(section.name)

    equipment_survey_name = fields.Char('Equipment Survey')

    @api.model
    def create(self, values):
        move = super(StockMove, self).create(values)
        sections = self.env['sale.order.line'].search([
            ('order_id', '=', move.sale_line_id.order_id.id), ('display_type', '=', 'line_section')])
        if len(sections) != 0:
            section = sections.filtered(lambda s: move.sale_line_id.sequence > s.sequence)[-1]
            move.equipment_survey_name = section.name
        return move


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    installer_id = fields.Many2one('res.partner', 'Installer')
    install_street = fields.Char(related='sale_id.install_street', readonly=False)
    install_city = fields.Char(related='sale_id.install_city', readonly=False)
    install_state_id = fields.Many2one(related='sale_id.install_state_id', readonly=False)
    install_zip = fields.Char(related='sale_id.install_zip', readonly=False)
    country_id = fields.Many2one(related='sale_id.country_id', readonly=False, default=233)
    special_note = fields.Text('Special Instructions')
    date_installed = fields.Datetime(string='Date Installed')
    installation_status = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
    ], 'Installation Status', default='pending')
    installation_desc = fields.Text('Installation Status', default='Pending')

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.state == 'assigned' and not self.installer_id and self.picking_type_code != 'incoming':
            raise UserError(_('Please assign an installer for this delivery.'))
        template = self.env['ir.model.data'].xmlid_to_res_id('crm_tbm_advanced.email_template_install_details')
        self.env['mail.template'].browse(template).send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_light')
        return super(StockPicking, self).button_validate()


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            price = line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = line_quantity * line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id)
            components.append({
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and self._get_bom_reference(line.child_bom_id) or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': line_quantity * line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id),
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
            total += sub_total
        return components, total


class ProductReplenish(models.TransientModel):
    _inherit = 'product.replenish'

    def launch_replenishment(self):
        uom_reference = self.product_id.uom_id
        self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference)
        if self.product_id.seller_ids and self.quantity < self.product_id.seller_ids.min_qty:
            raise UserError("The supplier's minimum qty for purchase order is " + str(self.product_id.seller_ids.min_qty))
        return super(ProductReplenish, self).launch_replenishment()
