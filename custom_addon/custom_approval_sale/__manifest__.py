{
    'name': 'Custom Approval Sale',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Approval workflow for Sales Orders ≥ 2M',
    'description': 'Sales Manager and CEO approvals for large deals',
    'depends': ['sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',  
    'author': 'Salman Ali Khan',
}
