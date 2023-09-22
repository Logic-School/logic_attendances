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
    class_id = fields.Many2one('logic.base.class',string="Class",required=True)
    coordinator = fields.Many2one("res.users",string="Coordinator",default=lambda self: self.env.user.id, readonly=True)
    # batch_id = fields.Many2one('logic.base.batch', string="Batch")
    student_attendances = fields.One2many('student.attendance','session_id', string="Student Attendances", default=False)
    students_added = fields.Boolean()
    # @api.onchange('batch_id')
    def create_attendances(self):
        if self.class_id:
            # self.student_attendances = False
            students = self.env['logic.students'].search([
                    ('class_id', '=', self.class_id.id)])
            self.env['student.attendance'].search([('session_id','=',self.id)]).unlink()
            if not students:
                raise UserError("No students found in the selected class!")
            for student in students:
                student_attendance = self.env['student.attendance'].create({
                    'student_id': student.id,
                    'morning_attendance':True,
                    'evening_attendance':True,
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