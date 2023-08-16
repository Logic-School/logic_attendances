from odoo import models, fields, api
from odoo.exceptions import UserError
import xlsxwriter
from datetime import timedelta
import base64
import os

class ReportWizard(models.TransientModel):
    _name="attendance.report.wizard"
    start_date = fields.Date()
    end_date = fields.Date()
    class_id = fields.Many2one('logic.base.class',string="Class Room")
    excel_file = fields.Binary(string="Excel Report")

    # batch_id = fields.Many2one('logic.base.batch', string="Batch")

    def get_dates(self):
        dates = []
        cur_date = self.start_date
        while(cur_date<=self.end_date):
            dates.append(cur_date)
            cur_date = (cur_date + timedelta(days=1))
        return dates
    
    def get_name_id_dict(self,students):
        names_and_ids = {}
        for student in students:
            names_and_ids[student.id] = student.name
        return names_and_ids
    def generate_report(self):
        days = []
        cur_date = self.start_date
        try:
            os.remove('/tmp/attendance_report.xlsx')
        except:
            pass
        workbook = xlsxwriter.Workbook('/tmp/attendance_report.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        header_format = workbook.add_format()
        header_format.set_align('center')
        header_format.set_bold()
        worksheet.write(1,0,'STUDENTS',header_format)
        students = self.env['logic.students'].search([('class_id','=',self.class_id.id)])
        names_and_ids = self.get_name_id_dict(students)
        data_dict = {}
        dates = self.get_dates()
        date_format = workbook.add_format()
        date_format.set_num_format('dd/mm/yy')
        # raise UserError(dates)
        date_col_ind = 1
        for date in dates:
            worksheet.write(1,date_col_ind,date,date_format)
            date_col_ind += 1
        
        for student in students:
            data_dict[student.id] = {}
            for date in dates:
                
                # check if the day is holiday or not
                test_obj = self.env['student.attendance'].search([('date','=',date)],limit=1)
                date=str(date) #converted to string as python dont accept date obj as dict key
                if not test_obj:
                    data_dict[student.id][date] = 'Holiday'
                    continue
                
                attendance_obj = self.env['student.attendance'].search([('date','=',date), ('student_id','=',student.id)])
                if not attendance_obj:
                    data_dict[student.id][date] = 'Absent'
                else:
                    if not attendance_obj.morning_attendance and not attendance_obj.evening_attendance:
                        data_dict[student.id][date] = 'Absent'  
                    elif attendance_obj.morning_attendance and attendance_obj.evening_attendance:
                        data_dict[student.id][date] = 'Present'
                    else:
                        data_dict[student.id][date] = 'Half Day'
        # raise UserError(data_dict)
        row_ind = 2
        for key in data_dict.keys():
            student_name = names_and_ids[key]
            worksheet.write(row_ind,0,student_name)
            col_ind = 1
            for value in data_dict[key].values():
                worksheet.write(row_ind,col_ind,value)
                col_ind+=1
            row_ind+=1
        
        worksheet.merge_range(first_row=0,last_row=0,first_col=1,last_col=col_ind,data='DATES', cell_format=header_format)
        workbook.close()
        excel_file = base64.b64encode(open('/tmp/attendance_report.xlsx','rb').read())
        self.excel_file = excel_file
        
        return {
            'name': 'Download Attendance Report',
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=attendance.report.wizard&id={}&field=excel_file&filename_field=test_report.xlsx&download=true'.format(
                self.id
            ),
            'target': 'self',
        }
        