# Odoo

Odoo is a suite of open-source business apps that cover all company needs: CRM, eCommerce, accounting, inventory, point of sale, project management, etc. Odoo’s unique value proposition is to be fully integrated, so apps can seamlessly work together.

## Features

- CRM & Sales
- Accounting & Finance
- Inventory & Manufacturing
- eCommerce & Website
- Project Management
- Human Resources
- Marketing Automation
- Point of Sale
- Reporting & Analytics

## Installation

Odoo requires Python 3 and PostgreSQL. You can install it via:

```bash
# Clone the repository
git clone https://github.com/odoo/odoo.git
cd odoo

# Install dependencies (on Debian/Ubuntu)
pip3 install -r requirements.txt

# Create PostgreSQL user
sudo -u postgres createuser --createdb --username postgres --no-createrole --no-superuser odoo

# Start Odoo
./odoo-bin
