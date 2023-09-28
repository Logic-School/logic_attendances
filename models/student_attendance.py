from odoo import fields,models,api

class StudentAttendance(models.Model):
    _name="student.attendance"
    student_id = fields.Many2one('logic.students',string="Student ID")
    student_name = fields.Char(related='student_id.name',strin="Student",store=True)
    session_id = fields.Many2one('attendance.session',string="Attendance Session",store=True)
    class_id = fields.Many2one('logic.base.class',related="session_id.class_id",store=True)
    # batch_id = fields.Many2one('logic.base.batch',relate="session_id.batch_id")
    date = fields.Date(related='session_id.date')
    morning_attendance = fields.Boolean(string="Morning Attendance")
    evening_attendance = fields.Boolean(string="Evening Attendance")
    absent_reason = fields.Char(string="Absent Reason")