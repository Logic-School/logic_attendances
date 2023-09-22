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
    filename = fields.Char(string="Filename")

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
        if not students:
            raise UserError("The selected class does not contain any students!")
        names_and_ids = self.get_name_id_dict(students)
        data_dict = {}
        
        dates = self.get_dates()
        date_format = workbook.add_format()
        date_format.set_num_format('dd/mm/yy')

        percentage_format = workbook.add_format({'num_format': '0.0%'})        # raise UserError(dates)

        date_col_ind = 1
        for date in dates:
            worksheet.write(1,date_col_ind,date,date_format)
            date_col_ind += 1
        
        total_working_days = 0
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
                    total_working_days+=1
        
        holiday_format = workbook.add_format()
        holiday_format.set_color('blue')
        present_format = workbook.add_format()
        present_format.set_color('green')
        half_day_format = workbook.add_format()
        half_day_format.set_color('orange')
        absent_format = workbook.add_format()
        absent_format.set_color('red')

        # raise UserError(data_dict)
        row_ind = 2
        for key in data_dict.keys():
            student_name = names_and_ids[key]
            worksheet.write(row_ind,0,student_name)
            col_ind = 1
            for value in data_dict[key].values():
                if value=='Holiday':
                    worksheet.write(row_ind,col_ind,value,holiday_format)
                elif value=='Half Day':
                    worksheet.write(row_ind,col_ind,value,half_day_format)
                elif value=='Present':
                    worksheet.write(row_ind,col_ind,value,present_format)
                elif value=='Absent':
                    worksheet.write(row_ind,col_ind,value,absent_format)
                col_ind+=1
            row_ind+=1

        worksheet.merge_range(first_row=0,last_row=0,first_col=col_ind,last_col=col_ind+2,data='TOTAL', cell_format=header_format)
        worksheet.merge_range(first_row=0,last_row=0,first_col=1,last_col=col_ind-1,data='DATES', cell_format=header_format)
        
        worksheet.write(1,col_ind,'Present Count',header_format)
        worksheet.set_column(col_ind,col_ind,20)
        worksheet.write(1,col_ind+1,'Working Days',header_format)
        worksheet.set_column(col_ind+1,col_ind+1,20)
        worksheet.write(1,col_ind+2,'Attendance Percentage',header_format)
        worksheet.set_column(col_ind+2,col_ind+2,20)

        col_address = self.get_col_address(col_ind)
        for row in range(2,row_ind):
            worksheet.write_formula(row, col_ind, f'COUNTIF(B{row+1}:{col_address}{row+1}, "Present") + COUNTIF(B{row+1}:{col_address}{row+1}, "Half Day")/2')
            worksheet.write_formula(row, col_ind+1, f'COUNTIF(B{row+1}:{col_address}{row+1}, "<>Holiday")')
            worksheet.write_formula(row, col_ind+2, f' (COUNTIF(B{row+1}:{col_address}{row+1}, "Present") + COUNTIF(B{row+1}:{col_address}{row+1}, "Half Day")/2) / (COUNTIF(B{row+1}:{col_address}{row+1}, "<>Holiday"))', cell_format=percentage_format)

        workbook.close()
        excel_file = base64.b64encode(open('/tmp/attendance_report.xlsx','rb').read())
        self.excel_file = excel_file
        self.filename = f"Attendance Report - {self.class_id.name} - {self.start_date} to {self.end_date}"
        
        return {
            'name': 'Download Attendance Report',
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=attendance.report.wizard&id={}&field=excel_file&filename_field=filename&download=true'.format(
                self.id
            ),
            'target': 'self',
        }
    

    def get_col_address(self,col_ind):
        alphabets = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        first_letter = alphabets[(col_ind//26)-1] if col_ind>26 else ''
        second_letter = alphabets[(col_ind%26)-1]
        # raise UserError(f'hello {col_ind}')

        return first_letter+second_letter
        