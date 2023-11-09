from odoo import models,fields, api
from odoo.exceptions import UserError
from datetime import datetime
class AttendanceSession(models.Model):
    _name = "attendance.session"
    def _compute_name(self):
        for record in self:
            zeroes = "0"*(5 - len(str(record.id)))
            record.name = "ATT"+zeroes+str(record.id)
    name = fields.Char(string="Name",compute="_compute_name")
    date = fields.Date(string="Date",default=datetime.today(), required=True)
    
    class_id = fields.Many2one('logic.base.class',string="Class",required=True,domain="[('batch_id','=',batch_id)]")
    coordinator = fields.Many2one("res.users",string="Coordinator",default=lambda self: self.env.user.id, readonly=True)
    batch_id = fields.Many2one('logic.base.batch', string="Batch",required=True)
    student_attendances = fields.One2many('student.attendance','session_id', string="Student Attendances", default=False)
    students_added = fields.Boolean()
    total_students_count = fields.Integer(compute="_compute_total_present_students_count")
    present_students_count = fields.Float(compute="_compute_total_present_students_count")
    present_total_display = fields.Char(compute="_compute_present_total_display",string="Attendance")
    session_type = fields.Selection([('offline','Offline'),('online','Online')],required=True)


    @api.onchange('session_type')
    def on_session_type_change(self):
        if self.session_type=='online':
            if self.student_attendances:
                for attendance in self.student_attendances:
                    attendance.morning_attendance = True
                    attendance.evening_attendance = True
                    attendance.full_attendance = True
            

    def _compute_total_present_students_count(self):
        for record in self:
            if record.student_attendances:
                record.total_students_count = len(record.student_attendances)
                present_count = 0
                for attendance in record.student_attendances:
                    if attendance.morning_attendance:
                        present_count+=0.5
                    if attendance.evening_attendance:
                        present_count+=0.5
                record.present_students_count = present_count
            else:
                record.total_students_count = 0
                record.present_students_count = 0
    @api.depends('present_students_count','total_students_count')
    def _compute_present_total_display(self):
        for record in self:
            if record.present_students_count and record.total_students_count:
                record.present_total_display = str(record.present_students_count) + ' / ' + str(record.total_students_count)
            else:
                record.present_total_display = '' 

    # @api.onchange('batch_id')
    def create_attendances(self):
        if self.class_id:
            # self.student_attendances = False
            class_allocated_stud_ids = []
            for stud_line in self.class_id.line_base_ids:
                class_allocated_stud_ids.append(stud_line.student_id.id)
            students = self.env['logic.students'].search([
                    ('id', 'in', class_allocated_stud_ids)])
            
            self.env['student.attendance'].search([('session_id','=',self.id)]).unlink()
            if not students:
                raise UserError("No students found in the selected class!")
            for student in students:
                student_attendance = self.env['student.attendance'].create({
                    'student_id': student.id,
                    'morning_attendance':True,
                    'evening_attendance':True,
                    'full_attendance': True,
                    'session_id': self.id,
                })
            self.student_attendances = self.env['student.attendance'].search([('session_id','=',self.id)])
            self.students_added = True
        else:
            raise UserError("You have to select a batch before adding students!")
        
    def reset_attendances(self):
        self.env['student.attendance'].search([('session_id','=',self.id)]).unlink()
        self.students_added = False

    @api.model
    def create(self,vals):
        test_obj = self.env['attendance.session'].sudo().search([('date','=',vals['date']), ('class_id','=',vals['class_id'])],limit=1)
        if test_obj:
            raise UserError(f"A Session record for this class on {vals['date']} already exists!")
        else:
            return super(AttendanceSession,self).create(vals)