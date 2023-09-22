{
    'name': "Attendances",
    'author': 'Rizwaan',
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'logic_base','admission','faculty'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_views.xml',
        'wizard/report_wizard_views.xml',
    ],
    'demo': [],
    'summary': "Attendances",
    'description': "",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}