from odoo import fields,models,api

class StudentAttendance(models.Model):
    _name="student.attendance"
    student_id = fields.Many2one('logic.students',string="Student ID")
    student_name = fields.Char(related='student_id.name',strin="Student",store=True)
    session_id = fields.Many2one('attendance.session',string="Attendance Session",store=True,ondelete='cascade')
    class_id = fields.Many2one('logic.base.class',related="session_id.class_id",store=True)
    # batch_id = fields.Many2one('logic.base.batch',relate="session_id.batch_id")
    attempt = fields.Selection(related="student_id.attempt")
    recording_status = fields.Selection(related="student_id.recording_status")
    email = fields.Char(related="student_id.email")
    phone_number = fields.Char(related="student_id.phone_number")
    parent_whatsapp = fields.Char(related="student_id.parent_whatsapp")

    date = fields.Date(related='session_id.date')
    morning_attendance = fields.Boolean(string="Morning Attendance")
    evening_attendance = fields.Boolean(string="Evening Attendance")
    absent_reason = fields.Char(string="Absent Reason")