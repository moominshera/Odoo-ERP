from odoo import models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, values):
        # Capture old prices BEFORE write
        old_prices = {}
        for line in self:
            old_prices[line.id] = line.price_unit

        # Perform the actual write
        result = super(SaleOrderLine, self).write(values)

        # Log price changes AFTER write
        if 'price_unit' in values:
            for line in self:
                old_price = old_prices.get(line.id)
                new_price = line.price_unit

                # Only log when price actually changes
                if old_price != new_price:
                    product_name = line.product_id.display_name

                    line.order_id.message_post(
                        body=f"Price changed for product '{product_name}' from {old_price} to {new_price}"
                    )

        return result
