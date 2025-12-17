{
    'name': 'CRM Procurement Task Pool',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Shared procurement task acquisition workflow',
    'description': """
Creates a shared procurement task when a lead reaches the Procurement stage.
Allows procurement team members to acquire the task with first-come locking
and full chatter tracking.
    """,
    'depends': ['crm', 'mail'],
    'data': [
        'views/crm_lead_view.xml',
],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'author': 'Salman Ali Khan',
}
