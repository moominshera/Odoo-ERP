{
    'name': 'Real Estate Construction Management',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Land, Building, Floor, Unit inventory linked to CRM, Sales, Purchase, Project and Accounting',
    'description': """
Construction Developer & Real Estate Management
=================================================
Links CRM leads to Sale Orders, Sale Orders to Property Units (via products),
Units to Buildings/Floors/Land parcels, Land to Purchase Orders (acquisition
cost) and Projects (construction), all rolled up through a shared analytic
account for per-parcel profitability.
    """,
    'author': 'Ume Developers',
    'depends': ['crm', 'sale_management', 'purchase', 'project', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'data/re_sequence.xml',
        'views/re_land_views.xml',
        'views/re_building_views.xml',
        'views/re_floor_views.xml',
        'views/re_unit_views.xml',
        'views/re_payment_plan_views.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'views/project_project_views.xml',
        'views/re_menus.xml',
    ],
    'demo': [
        'data/re_demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
