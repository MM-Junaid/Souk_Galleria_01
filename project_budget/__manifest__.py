{
    'name': "Project Budget",
    'summary': "Adds budget management to projects.",
    'depends': [
        'purchase',
        'project',
        'account',
        'hr_timesheet',
    ],
    'data': [

        'security/ir.model.access.csv',
        'views/project.xml',
        # 'report/purchase_order_template.xml',
        'report/report_menu.xml',
        'report/report_purchase_order.xml',

    ]
}
