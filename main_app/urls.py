"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views, proctor_views, event_views, message_views, resource_views, management_views, auth_views, admission_views, payroll_views, alumni_views, chat_views, placement_views, lms_views, analytics_views, performance_views, document_views, parent_views, gemini_views, public_views

urlpatterns = [
    # New Clean Auth System (Single-Page Login with OTP)
    path("", auth_views.login_with_otp, name='login_with_otp'),
    path("login/", auth_views.login_with_otp, name='login_page'),  # Alias for compatibility
    path("user_login/", auth_views.login_with_otp, name='user_login'),  # Alias for old templates
    path("verify_otp/", views.verify_otp, name='verify_otp'),  # OTP verification endpoint
    path("logout/", auth_views.logout_view, name='logout'),
    path("logout_user/", auth_views.logout_view, name='user_logout'),  # Alias
    path("admin/logout/", auth_views.logout_view, name='admin_logout'),  # Alias for HOD navigation
    path("student/logout/", auth_views.logout_view, name='student_logout'),  # Alias for student navigation
    path("staff/logout/", auth_views.logout_view, name='staff_logout'),  # Alias for staff navigation
    
    # Action button URLs
    path("admin/student/<int:student_id>/view/", hod_views.view_student_detail, name='view_student_detail'),
    path("admin/student/<int:student_id>/edit/", hod_views.edit_student, name='edit_student'),
    path("admin/staff/<int:staff_id>/view/", hod_views.view_staff_detail, name='view_staff_detail'),
    path("admin/staff/<int:staff_id>/edit/", hod_views.edit_staff, name='edit_staff'),
    
    # Public Data Access (No authentication required)
    path("public/", views.public_data, name='public_data'),
    path("public/roll/", public_views.public_roll_verify, name='public_roll_verify'),
    path("public/student/info/", public_views.public_student_info, name='public_student_info'),
    path("public/clear/", public_views.clear_public_session, name='clear_public_session'),
    
    # Utility endpoints
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("serviceworker.js", views.serve_service_worker, name='service_worker'),
    path("admin/home/", hod_views.admin_home, name='hod_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("course/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("profile/view/", hod_views.admin_view_profile, name="view_profile"),  # Alias
    path("profile/edit/", hod_views.admin_view_profile, name="edit_profile"),  # Alias (same view for now)
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    # URL aliases for navigation consistency
    path("student/leave/view/", hod_views.view_student_leave, name="student_leave_view"),  # Alias
    path("staff/leave/view/", hod_views.view_staff_leave, name="staff_leave_view"),  # Alias
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("student/attendance/view/", hod_views.admin_view_attendance, name="student_attendance_view"),  # Alias
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>",
         hod_views.edit_subject, name='edit_subject'),
    
    # Proctor Management (HOD)
    path("admin/proctors/manage/", hod_views.manage_proctors, name='manage_proctors'),
    path("admin/proctor/assign/", hod_views.assign_proctor_to_student, name='assign_proctor_to_student'),
    path("admin/proctor/remove/", hod_views.remove_proctor_assignment, name='remove_proctor_assignment'),

    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/bulk-import/", staff_views.bulk_attendance_import,
         name='bulk_attendance_import'),
    path("staff/attendance/qr-generate/", staff_views.generate_attendance_qr,
         name='generate_attendance_qr'),
    path("staff/attendance/analytics/", staff_views.attendance_analytics,
         name='staff_attendance_analytics'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/bulk-import/", staff_views.bulk_marks_import, name='bulk_marks_import'),
    path("staff/result/cgpa/<int:student_id>/", staff_views.calculate_student_cgpa, name='calculate_student_cgpa'),
    path("staff/result/marksheet/<int:student_id>/", staff_views.generate_marksheet_pdf, name='generate_marksheet_pdf'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),



    # Student
    path("student/home/", student_views.student_home, name='student_home'),
    path("student/view/attendance/", student_views.student_view_attendance,
         name='student_view_attendance'),
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),
    
    # Additional Student URLs for navigation (primary URLs for students)
    path("student/materials/", student_views.view_materials, name='view_materials'),
    path("student/assignments/", student_views.view_assignments, name='view_assignments'),
    path("student/submissions/", student_views.view_submissions, name='view_submissions'),
    path("student/online-exam/", student_views.view_online_exam, name='view_online_exam'),
    path("student/events/", student_views.view_events, name='view_events'),
    
    # Proctor URLs
    path("proctor/home/", proctor_views.proctor_home, name='proctor_home'),
    path("proctor/students/", proctor_views.proctor_view_students, name='proctor_view_students'),
    path("proctor/student/<int:student_id>/", proctor_views.proctor_student_details, name='proctor_student_details'),
    path("proctor/absentee/", proctor_views.proctor_absentee_list, name='proctor_absentee_list'),
    path("proctor/profile/", proctor_views.proctor_view_profile, name='proctor_view_profile'),
    path("proctor/messages/", proctor_views.proctor_messages, name='proctor_messages'),
    path("proctor/message/send/", proctor_views.proctor_send_message, name='proctor_send_message'),
    path("proctor/message/mark_read/<int:message_id>/", proctor_views.proctor_mark_message_read, name='proctor_mark_message_read'),
    
    # Event URLs - Admin
    path("admin/events/", event_views.admin_view_events, name='admin_view_events'),
    path("admin/event/create/", event_views.admin_create_event, name='admin_create_event'),
    path("admin/event/approve/", event_views.admin_approve_event, name='admin_approve_event'),
    
    # Event URLs - Staff
    path("staff/events/", event_views.staff_view_events, name='staff_view_events'),
    path("staff/event/create/", event_views.staff_create_event, name='staff_create_event'),
    
    # Event URLs - Student
    path("student/events/", event_views.student_view_events, name='student_view_events'),
    path("student/event/register/", event_views.student_register_event, name='student_register_event'),
    path("student/event/unregister/", event_views.student_unregister_event, name='student_unregister_event'),
    
    # Event URLs - Proctor
    path("proctor/events/", event_views.proctor_view_events, name='proctor_view_events'),
    
    # Messaging URLs (Common for all user types)
    path("message/send/", message_views.send_message, name='send_message'),
    path("messages/", message_views.view_messages, name='view_messages'),
    path("message/<int:message_id>/", message_views.view_message, name='view_message'),
    path("message/<int:message_id>/reply/", message_views.reply_message, name='reply_message'),
    path("message/<int:message_id>/delete/", message_views.delete_message, name='delete_message'),
    path("message/<int:message_id>/mark_read/", message_views.mark_message_read, name='mark_message_read'),
    path("messages/mark_all_read/", message_views.mark_all_read, name='mark_all_read'),
    
    # Alias URLs for different user types
    path("admin/messages/", message_views.view_messages, name='admin_messages'),
    path("staff/messages/", message_views.view_messages, name='staff_messages'),
    path("student/messages/", message_views.view_messages, name='student_messages'),
    
    # Study Materials - Staff
    path("staff/material/upload/", resource_views.staff_upload_material, name='staff_upload_material'),
    path("staff/materials/", resource_views.staff_view_materials, name='staff_view_materials'),
    
    # Study Materials - Student
    path("student/resources/", resource_views.student_view_resources, name='student_view_resources'),
    path("student/bookmarks/", resource_views.student_view_bookmarks, name='student_view_bookmarks'),
    path("student/resource/bookmark/", resource_views.toggle_bookmark, name='toggle_bookmark'),
    path("student/resource/rate/", resource_views.rate_material, name='rate_material'),
    path("resource/download/<int:material_id>/", resource_views.download_material, name='download_material'),
    path("student/resources/bulk-download/", resource_views.bulk_download_materials, name='bulk_download_materials'),
    
    # Study Materials - Admin
    path("admin/resources/", resource_views.admin_view_resources, name='admin_view_resources'),
    path("admin/resource/stats/", resource_views.admin_resource_stats, name='admin_resource_stats'),
    
    # Assignments - Staff
    path("staff/assignment/create/", resource_views.staff_create_assignment, name='staff_create_assignment'),
    path("staff/assignments/", resource_views.staff_view_assignments, name='staff_view_assignments'),
    path("staff/assignment/<int:assignment_id>/submissions/", resource_views.staff_view_submissions, name='staff_view_submissions'),
    path("staff/submission/grade/", resource_views.staff_grade_submission, name='staff_grade_submission'),
    
    # Assignments - Student
    path("student/assignments/", resource_views.student_view_assignments, name='student_view_assignments'),
    path("student/assignment/<int:assignment_id>/submit/", resource_views.student_submit_assignment, name='student_submit_assignment'),
    
    # Assignments - Admin
    path("admin/assignments/", resource_views.admin_view_all_assignments, name='admin_view_all_assignments'),
    
    # Announcements
    path("admin/announcement/create/", resource_views.admin_create_announcement, name='admin_create_announcement'),
    path("announcements/", resource_views.view_announcements, name='view_announcements'),
    path("admin/announcements/", resource_views.view_announcements, name='admin_view_announcements'),
    path("staff/announcements/", resource_views.view_announcements, name='staff_view_announcements'),
    path("student/announcements/", resource_views.view_announcements, name='student_view_announcements'),
    
    # Discussion Forum
    path("subject/<int:subject_id>/discussions/", resource_views.view_discussions, name='view_discussions'),
    path("subject/<int:subject_id>/discussion/create/", resource_views.create_discussion, name='create_discussion'),
    path("discussion/<int:discussion_id>/", resource_views.view_discussion, name='view_discussion'),
    path("discussion/reply/", resource_views.reply_discussion, name='reply_discussion'),
    
    # ==================== EXAM CELL PANEL ====================
    # Exam Management - HOD
    path("admin/exams/manage/", hod_views.manage_exams, name='manage_exams'),
    path("admin/exam/add/", hod_views.add_exam, name='add_exam'),
    path("admin/exam/<int:exam_id>/schedule/", hod_views.manage_exam_schedule, name='manage_exam_schedule'),
    path("admin/exam/<int:exam_id>/schedule/add/", hod_views.add_exam_schedule, name='add_exam_schedule'),
    path("admin/exam/schedule/<int:schedule_id>/invigilators/", hod_views.assign_invigilators, name='assign_invigilators'),
    path("admin/exam/<int:exam_id>/admit-cards/generate/", hod_views.generate_admit_cards, name='generate_admit_cards'),
    
    # Results - HOD
    path("admin/results/manage/", hod_views.manage_results, name='manage_results'),
    path("admin/result/semester/add/", hod_views.add_semester_result, name='add_semester_result'),
    path("admin/result/<int:result_id>/publish/", hod_views.publish_results, name='publish_results'),
    
    # Exam Schedule - Student
    path("student/timetable/", student_views.student_view_timetable, name='student_view_timetable'),
    path("student/exams/schedule/", student_views.student_view_exam_schedule, name='student_view_exam_schedule'),
    path("student/exam/<int:exam_id>/admit-card/", student_views.student_download_admit_card, name='student_download_admit_card'),
    
    # Results - Student
    path("student/results/", student_views.student_view_semester_results, name='student_view_semester_results'),
    path("student/result/<int:result_id>/detail/", student_views.student_view_semester_detail, name='student_view_semester_detail'),
    
    # ==================== PLACEMENT PANEL ====================
    # Company Management - HOD
    path("admin/companies/manage/", hod_views.manage_companies, name='manage_companies'),
    path("admin/company/add/", hod_views.add_company, name='add_company'),
    path("admin/company/<int:company_id>/edit/", hod_views.edit_company, name='edit_company'),
    
    # Placement Drives - HOD
    path("admin/placements/manage/", hod_views.manage_placement_drives, name='manage_placement_drives'),
    path("admin/placement/drive/add/", hod_views.add_placement_drive, name='add_placement_drive'),
    path("admin/placement/<int:drive_id>/applications/", hod_views.view_placement_applications, name='view_placement_applications'),
    path("admin/placement/application/<int:app_id>/update/", hod_views.update_application_status, name='update_application_status'),
    
    # Placements - Student
    path("student/placements/", student_views.student_view_placement_drives, name='student_view_placement_drives'),
    path("student/placement/<int:drive_id>/apply/", student_views.student_apply_placement, name='student_apply_placement'),
    path("student/placements/my-applications/", student_views.student_my_placement_applications, name='student_my_placement_applications'),
    
    # ==================== FEE MANAGEMENT PANEL ====================
    # Fee Structure - HOD
    path("admin/fees/structure/manage/", hod_views.manage_fee_structure, name='manage_fee_structure'),
    path("admin/fees/structure/add/", hod_views.add_fee_structure, name='add_fee_structure'),
    path("admin/fees/structure/<int:structure_id>/edit/", hod_views.edit_fee_structure, name='edit_fee_structure'),
    
    # Fee Payments - HOD
    path("admin/fees/payments/", hod_views.view_fee_payments, name='view_fee_payments'),
    path("admin/fees/payment/record/", hod_views.record_fee_payment, name='record_fee_payment'),
    path("admin/fees/receipt/<int:payment_id>/", hod_views.generate_fee_receipt, name='generate_fee_receipt'),
    path("admin/fees/defaulters/", hod_views.fee_defaulters, name='fee_defaulters'),
    
    # Fee - Student
    path("student/fees/structure/", student_views.student_view_fee_structure, name='student_view_fee_structure'),
    path("student/fees/receipts/", student_views.student_fee_receipts, name='student_fee_receipts'),
    
    # ==================== GRIEVANCE PANEL ====================
    # Student Grievances
    path("student/grievance/submit/", student_views.student_submit_grievance, name='student_submit_grievance'),
    path("student/grievances/", student_views.student_my_grievances, name='student_my_grievances'),
    
    # HOD Grievance Management
    path("admin/grievances/", hod_views.view_grievances, name='view_grievances'),
    path("admin/grievance/<int:grievance_id>/assign/", hod_views.assign_grievance, name='assign_grievance'),
    path("admin/grievance/<int:grievance_id>/resolve/", hod_views.resolve_grievance, name='resolve_grievance'),
    
    # ==================== TRANSPORT MANAGEMENT ====================
    # HOD Transport Management
    path("admin/transport/manage/", hod_views.manage_transport, name='manage_transport'),
    path("admin/transport/add/", hod_views.add_transport, name='add_transport'),
    path("admin/transport/<int:transport_id>/edit/", hod_views.edit_transport, name='edit_transport'),

    # ==================== ADMISSION MANAGEMENT PANEL ====================
    # Admission Dashboard - HOD/Management
    path("admin/admissions/", admission_views.admission_dashboard, name='admission_dashboard'),
    path("admin/admissions/applications/", admission_views.review_applications, name='review_applications'),
    path("admin/admissions/application/<int:application_id>/", admission_views.view_application, name='view_application'),
    path("admin/admissions/application/<int:application_id>/decision/", admission_views.make_decision, name='make_decision'),
    path("admin/admissions/document/<int:document_id>/verify/", admission_views.verify_documents, name='verify_documents'),
    path("admin/admissions/analytics/", admission_views.admission_statistics, name='admission_analytics'),
    path("admin/admissions/bulk-admit/", admission_views.bulk_admit_students, name='bulk_admit_students'),
    
    # Student Admission Application
    path("student/admission/apply/", admission_views.apply_admission, name='apply_admission'),
    path("student/admission/application/<int:application_id>/", admission_views.view_application, name='view_application'),
    path("student/admission/application/<int:application_id>/documents/", admission_views.upload_documents, name='upload_documents'),
    path("student/admission/track/", admission_views.track_application, name='track_application'),
    
    # AJAX Endpoints
    path("api/admissions/programs/", admission_views.get_programs_for_session, name='get_programs_for_session'),
    path("api/admissions/check-status/", admission_views.check_application_status, name='check_application_status'),

    # ==================== PAYROLL & HR MANAGEMENT PANEL ====================
    # Payroll Dashboard - HOD/Management
    path("admin/payroll/", payroll_views.payroll_dashboard, name='payroll_dashboard'),
    path("admin/payroll/salary-structure/", payroll_views.configure_salary_structure, name='configure_salary_structure'),
    path("admin/payroll/employee-salary/", payroll_views.assign_employee_salary, name='assign_employee_salary'),
    path("admin/payroll/process/", payroll_views.process_payroll, name='process_payroll'),
    path("admin/payroll/payslips/", payroll_views.view_payslips, name='view_payslips'),
    path("admin/payroll/payslip/<uuid:payslip_id>/", payroll_views.view_payslip_detail, name='view_payslip_detail'),
    path("admin/payroll/tax-declarations/", payroll_views.tax_declaration_management, name='tax_declaration_management'),
    path("admin/payroll/tax-document/<int:declaration_id>/verify/", payroll_views.verify_tax_document, name='verify_tax_document'),
    path("admin/payroll/leave-balances/", payroll_views.leave_balance_management, name='leave_balance_management'),
    path("admin/payroll/attendance/", payroll_views.attendance_register, name='attendance_register'),
    path("admin/payroll/bonuses/", payroll_views.bonus_management, name='bonus_management'),
    path("admin/payroll/loans/", payroll_views.loan_management, name='loan_management'),
    path("admin/payroll/loan/<int:loan_id>/approve/", payroll_views.approve_loan, name='approve_loan'),
    path("admin/payroll/analytics/", payroll_views.payroll_analytics, name='payroll_analytics'),
    
    # Employee Self-Service
    path("staff/payroll/", payroll_views.employee_self_service, name='employee_self_service'),
    
    # AJAX Endpoints for Payroll
    path("api/payroll/employee-salary/<int:employee_id>/", payroll_views.get_employee_salary_ajax, name='get_employee_salary_ajax'),
    path("api/payroll/calculate-salary/", payroll_views.calculate_salary_ajax, name='calculate_salary_ajax'),
    path("api/payroll/summary/", payroll_views.payroll_summary_ajax, name='payroll_summary_ajax'),

    # ==================== ALUMNI MANAGEMENT PANEL ====================
    # Alumni Dashboard - HOD/Management
    path("admin/alumni/", alumni_views.alumni_dashboard, name='alumni_dashboard'),
    path("admin/alumni/directory/", alumni_views.alumni_directory, name='alumni_directory'),
    path("admin/alumni/profile/<int:alumni_id>/", alumni_views.alumni_profile, name='alumni_profile'),
    path("admin/alumni/events/", alumni_views.alumni_events, name='alumni_events'),
    path("admin/alumni/event/<uuid:event_id>/", alumni_views.alumni_event_detail, name='alumni_event_detail'),
    path("admin/alumni/donations/", alumni_views.alumni_donations, name='alumni_donations'),
    path("admin/alumni/donation/<uuid:campaign_id>/", alumni_views.alumni_donation_detail, name='alumni_donation_detail'),
    path("admin/alumni/mentorship/", alumni_views.alumni_mentorship, name='alumni_mentorship'),
    path("admin/alumni/newsletter/", alumni_views.alumni_newsletter, name='alumni_newsletter'),
    path("admin/alumni/analytics/", alumni_views.alumni_analytics, name='alumni_analytics'),
    
    # Student/Alumni Access
    path("student/mentorship/request/", alumni_views.mentorship_request, name='mentorship_request'),
    path("alumni/jobs/", alumni_views.alumni_jobs, name='alumni_jobs'),
    
    # AJAX Endpoints for Alumni
    path("api/alumni/mentors/", alumni_views.get_available_mentors_ajax, name='get_available_mentors_ajax'),
    path("api/alumni/stats/", alumni_views.alumni_stats_ajax, name='alumni_stats_ajax'),
    path("admin/transport/allocations/", hod_views.transport_allocations, name='transport_allocations'),
    path("admin/transport/allocate/", hod_views.allocate_transport, name='allocate_transport'),
    
    # Student Transport
    path("student/transport/my-details/", student_views.student_my_transport, name='student_my_transport'),
    
    # ==================== LIBRARY MANAGEMENT ====================
    # HOD Library Management
    path("admin/library/manage/", hod_views.manage_library, name='manage_library'),
    path("admin/library/book/add/", hod_views.add_library_book, name='add_library_book'),
    path("admin/library/book/<int:book_id>/edit/", hod_views.edit_library_book, name='edit_library_book'),
    path("admin/library/issues/", hod_views.library_issues, name='library_issues'),
    path("admin/library/book/issue/", hod_views.issue_library_book, name='issue_library_book'),
    path("admin/library/issue/<int:issue_id>/return/", hod_views.return_library_book, name='return_library_book'),
    
    # Student Library
    path("student/library/search/", student_views.student_search_books, name='student_search_books'),
    path("student/library/my-issues/", student_views.student_my_library_issues, name='student_my_library_issues'),
    
    # ==================== HOSTEL MANAGEMENT ====================
    # HOD Hostel Management
    path("admin/hostels/manage/", hod_views.manage_hostels, name='manage_hostels'),
    path("admin/hostel/add/", hod_views.add_hostel, name='add_hostel'),
    path("admin/hostel/allocations/", hod_views.hostel_allocations, name='hostel_allocations'),
    path("admin/hostel/allocate/", hod_views.allocate_hostel, name='allocate_hostel'),
    path("admin/hostel/visitors/", hod_views.hostel_visitor_logs, name='hostel_visitor_logs'),
    
    # Student Hostel
    path("student/hostel/my-details/", student_views.student_my_hostel, name='student_my_hostel'),
    
    # ==================== DIGITAL LOCKER SYSTEM ====================
    # Student Document Locker
    path("student/documents/", document_views.student_document_locker, name='student_document_locker'),
    path("student/documents/category/<str:category>/", document_views.view_documents_by_category, name='view_documents_by_category'),
    path("student/documents/upload/", document_views.upload_document, name='upload_document'),
    path("student/documents/<int:document_id>/", document_views.view_document_detail, name='view_document_detail'),
    path("student/documents/<int:document_id>/download/", document_views.download_document, name='download_document'),
    path("student/documents/<int:document_id>/delete/", document_views.delete_document, name='delete_document'),
    path("student/documents/search/", document_views.search_my_documents, name='search_my_documents'),
    path("student/documents/important/", document_views.view_important_documents, name='view_important_documents'),
    path("student/documents/bulk-download/", document_views.bulk_download_my_documents, name='bulk_download_my_documents'),
    path("student/documents/<int:document_id>/toggle-important/", document_views.toggle_important, name='toggle_important'),
    
    # Admin Document Management
    path("admin/documents/all/", document_views.admin_view_all_documents, name='admin_view_all_documents'),
    path("admin/documents/statistics/", document_views.admin_document_statistics, name='admin_document_statistics'),
    
    # ==================== SCHOLARSHIP MANAGEMENT ====================
    # HOD Scholarship Management
    path("admin/scholarships/manage/", hod_views.manage_scholarships, name='manage_scholarships'),
    path("admin/scholarship/add/", hod_views.add_scholarship, name='add_scholarship'),
    path("admin/scholarship/applications/", hod_views.scholarship_applications, name='scholarship_applications'),
    path("admin/scholarship/application/<int:app_id>/review/", hod_views.review_scholarship_application, name='review_scholarship_application'),
    path("admin/scholarship/application/<int:app_id>/disburse/", hod_views.disburse_scholarship, name='disburse_scholarship'),
    
    # Student Scholarships
    path("student/scholarships/", student_views.student_view_scholarships, name='student_view_scholarships'),
    path("student/scholarship/<int:scholarship_id>/apply/", student_views.student_apply_scholarship, name='student_apply_scholarship'),
    path("student/scholarships/my-applications/", student_views.student_my_scholarship_applications, name='student_my_scholarship_applications'),
    
    # ==================== TIMETABLE MANAGEMENT ====================
    # HOD Timetable Management
    path("admin/timetable/manage/", hod_views.manage_timetable, name='manage_timetable'),
    path("admin/timetable/add/", hod_views.add_timetable, name='add_timetable'),
    
    # ==================== DEPARTMENT & PROGRAM MANAGEMENT ====================
    # Department Management
    path("admin/departments/manage/", hod_views.manage_departments, name='manage_departments'),
    path("admin/department/add/", hod_views.add_department, name='add_department'),
    path("admin/department/<int:dept_id>/edit/", hod_views.edit_department, name='edit_department'),
    
    # Program Management
    path("admin/programs/manage/", hod_views.manage_programs, name='manage_programs'),
    path("admin/program/add/", hod_views.add_program, name='add_program'),
    path("admin/program/<int:program_id>/edit/", hod_views.edit_program, name='edit_program'),
    
    # ==================== HOD/ADMIN USER MANAGEMENT ====================
    path("admin/manage-admins/", hod_views.manage_admins, name='manage_admins'),
    path("admin/add-admin/", hod_views.add_admin, name='add_admin'),
    path("admin/edit-admin/<int:admin_id>/", hod_views.edit_admin, name='edit_admin'),
    path("admin/delete-admin/<int:admin_id>/", hod_views.delete_admin, name='delete_admin'),
    
    # Analytics Dashboard
    path("admin/analytics/", hod_views.admin_analytics_dashboard, name='admin_analytics_dashboard'),
    
    # AI-Powered Analytics
    path("admin/ai-insights/", hod_views.ai_student_insights, name='ai_student_insights'),
    path("admin/ai-report/generate/", hod_views.generate_ai_report, name='generate_ai_report'),
    
    # ==================== STAFF/FACULTY PANEL FEATURES ====================
    # Staff Timetable
    path("staff/my-timetable/", staff_views.staff_view_timetable, name='staff_view_timetable'),
    
    # Staff Exam Duties
    path("staff/exam-duties/", staff_views.staff_my_exam_duties, name='staff_my_exam_duties'),
    path("staff/exam/schedule/<int:schedule_id>/upload-question-paper/", staff_views.staff_upload_question_paper, name='staff_upload_question_paper'),
    path("staff/exam/schedule/<int:schedule_id>/upload-answer-key/", staff_views.staff_upload_answer_key, name='staff_upload_answer_key'),
    
    # Staff Result Entry
    path("staff/marks/enter/", staff_views.staff_enter_marks, name='staff_enter_marks'),
    path("staff/results/view/", staff_views.staff_view_results, name='staff_view_results'),
    
    # Additional Staff URLs for navigation
    path("staff/materials/upload/", staff_views.upload_material, name='upload_material'),
    path("staff/materials/", staff_views.view_materials, name='staff_view_materials_legacy'),
    path("staff/assignments/create/", staff_views.create_assignment, name='create_assignment'),
    path("staff/assignments/", staff_views.view_assignments, name='staff_view_assignments_legacy'),
    path("staff/submissions/", staff_views.view_submissions, name='staff_view_submissions_legacy'),
    path("staff/exams/create/", staff_views.create_online_exam, name='create_online_exam'),
    path("staff/exams/", staff_views.my_online_exams, name='my_online_exams'),
    
    # Staff Library (for Librarians)
    path("staff/library/issue-return/", staff_views.staff_library_issue_return, name='staff_library_issue_return'),
    
    # Staff Placement (for Coordinators)
    path("staff/placements/manage/", staff_views.staff_manage_placements, name='staff_manage_placements'),
    
    # Staff Grievances
    path("staff/grievances/assigned/", staff_views.staff_my_assigned_grievances, name='staff_my_assigned_grievances'),
    path("staff/grievance/<int:grievance_id>/resolve/", staff_views.staff_resolve_grievance, name='staff_resolve_grievance'),
    
    # ==================== ADDITIONAL STUDENT FEATURES ====================
    # Library - Student
    path("student/library/my-scholarships/", student_views.student_view_scholarships, name='student_view_scholarships_dup'),
    path("student/scholarship/my-apps/", student_views.student_my_scholarship_applications, name='student_my_scholarship_apps_dup'),
    path("student/library/books/", student_views.student_search_books, name='student_library_search'),
    path("student/library/issues/", student_views.student_my_library_issues, name='student_library_issues'),
    
    # Transport & Hostel - Student
    path("student/my-transport/", student_views.student_my_transport, name='student_transport_details'),
    path("student/my-hostel/", student_views.student_my_hostel, name='student_hostel_details'),
    
    # ==================== PARENT PORTAL ====================
    # Parent Dashboard
    path("parent/home/", parent_views.parent_home, name='parent_home'),
    path("parent/profile/", parent_views.parent_view_profile, name='parent_view_profile'),
    path("parent/link-student/", parent_views.link_student, name='link_student'),
    path("parent/child/<int:student_id>/", parent_views.view_child_detail, name='view_child_detail'),
    path("parent/child/<int:student_id>/attendance/", parent_views.view_child_attendance, name='view_child_attendance'),
    path("parent/child/<int:student_id>/results/", parent_views.view_child_results, name='view_child_results'),
    path("parent/child/<int:student_id>/assignments/", parent_views.view_child_assignments, name='view_child_assignments'),
    path("parent/child/<int:student_id>/fees/", parent_views.view_child_fees, name='view_child_fees'),
    path("parent/child/<int:student_id>/message-teacher/", parent_views.send_message_to_teacher, name='send_message_to_teacher'),
    
    # ==================== MANAGEMENT PANEL ====================
    # Management Dashboard
    path("management/home/", management_views.management_home, name='management_home'),
    path("management/profile/", management_views.management_view_profile, name='management_view_profile'),
    
    # Management - Transport
    path("management/transport/manage/", management_views.manage_transport, name='management_transport'),
    path("management/transport/add/", management_views.add_transport, name='management_add_transport'),
    path("management/transport/<int:transport_id>/edit/", management_views.edit_transport, name='management_edit_transport'),
    path("management/transport/allocations/", management_views.transport_allocations, name='management_transport_allocations'),
    path("management/transport/allocate/", management_views.allocate_transport, name='management_allocate_transport'),
    
    # Management - Hostel
    path("management/hostels/manage/", management_views.manage_hostels, name='management_hostels'),
    path("management/hostel/add/", management_views.add_hostel, name='management_add_hostel'),
    path("management/hostel/allocations/", management_views.hostel_allocations, name='management_hostel_allocations'),
    path("management/hostel/allocate/", management_views.allocate_hostel, name='management_allocate_hostel'),
    path("management/hostel/visitors/", management_views.hostel_visitor_logs, name='management_hostel_visitors'),
    
    # Management - Library
    path("management/library/manage/", management_views.manage_library, name='management_library'),
    path("management/library/book/add/", management_views.add_library_book, name='management_add_library_book'),
    path("management/library/book/<int:book_id>/edit/", management_views.edit_library_book, name='management_edit_library_book'),
    path("management/library/issues/", management_views.library_issues, name='management_library_issues'),
    path("management/library/book/issue/", management_views.issue_library_book, name='management_issue_library_book'),
    path("management/library/issue/<int:issue_id>/return/", management_views.return_library_book, name='management_return_library_book'),
    
    # Management - Fees
    path("management/fees/structure/manage/", management_views.manage_fee_structure, name='management_fee_structure'),
    path("management/fees/structure/add/", management_views.add_fee_structure, name='management_add_fee_structure'),
    path("management/fees/structure/<int:structure_id>/edit/", management_views.edit_fee_structure, name='management_edit_fee_structure'),
    path("management/fees/payments/", management_views.view_fee_payments, name='management_fee_payments'),
    path("management/fees/payment/record/", management_views.record_fee_payment, name='management_record_fee_payment'),
    path("management/fees/defaulters/", management_views.fee_defaulters, name='management_fee_defaulters'),
    
    # Management - Scholarships
    path("management/scholarships/manage/", management_views.manage_scholarships, name='management_scholarships'),
    path("management/scholarship/add/", management_views.add_scholarship, name='management_add_scholarship'),
    path("management/scholarship/applications/", management_views.scholarship_applications, name='management_scholarship_applications'),
    path("management/scholarship/application/<int:app_id>/review/", management_views.review_scholarship_application, name='management_review_scholarship'),
    path("management/scholarship/application/<int:app_id>/disburse/", management_views.disburse_scholarship, name='management_disburse_scholarship'),
    
    # Management - Grievances
    path("management/grievances/", management_views.view_grievances, name='management_grievances'),
    path("management/grievance/<int:grievance_id>/assign/", management_views.assign_grievance, name='management_assign_grievance'),
    path("management/grievance/<int:grievance_id>/resolve/", management_views.resolve_grievance, name='management_resolve_grievance'),


    # ============================================================================
    # NEW ECAP FEATURES - HOD URLs
    # ============================================================================
    
    # Online Examination
    path('admin/online_exams/', hod_views.manage_online_exams, name='manage_online_exams'),
    path('admin/online_exams/create/', hod_views.create_online_exam, name='create_online_exam'),
    path('admin/online_exams/<int:exam_id>/questions/', hod_views.add_exam_questions, name='add_exam_questions'),
    
    # Certificates
    path('admin/certificates/', hod_views.manage_certificates, name='manage_certificates'),
    path('admin/certificates/issue/', hod_views.issue_certificate, name='issue_certificate'),
    
    # Alumni
    path('admin/alumni/', hod_views.manage_alumni, name='manage_alumni'),
    
    # Internships
    path('admin/internships/', hod_views.manage_internships, name='manage_internships'),
    path('admin/internships/<int:internship_id>/approve/', hod_views.approve_internship, name='approve_internship'),
    
    # Sports & Activities
    path('admin/activities/', hod_views.manage_sports_activities, name='manage_sports_activities'),
    path('admin/activities/create/', hod_views.create_activity, name='create_activity'),
    
    # Gate Pass
    path('admin/gate_passes/', hod_views.manage_gate_passes, name='manage_gate_passes'),
    path('admin/gate_passes/<int:pass_id>/approve/', hod_views.approve_gate_pass, name='approve_gate_pass'),
    
    # Disciplinary Actions
    path('admin/disciplinary/', hod_views.manage_disciplinary_actions, name='manage_disciplinary_actions'),
    path('admin/disciplinary/add/', hod_views.add_disciplinary_action, name='add_disciplinary_action'),
    
    # Anti-Ragging
    path('admin/ragging/', hod_views.manage_ragging_incidents, name='manage_ragging_incidents'),
    path('admin/ragging/<int:incident_id>/assign/', hod_views.assign_ragging_investigator, name='assign_ragging_investigator'),
    
    # Student Council
    path('admin/council/', hod_views.manage_student_council, name='manage_student_council'),
    path('admin/council/add/', hod_views.add_council_member, name='add_council_member'),
    
    # Classroom Management
    path('admin/classrooms/', hod_views.manage_classrooms, name='manage_classrooms'),
    path('admin/classrooms/add/', hod_views.add_classroom, name='add_classroom'),
    path('admin/classrooms/<int:classroom_id>/edit/', hod_views.edit_classroom, name='edit_classroom'),
    path('admin/classrooms/bookings/', hod_views.manage_classroom_bookings, name='manage_classroom_bookings'),
    path('admin/classrooms/book/', hod_views.book_classroom, name='book_classroom'),
    path('admin/classrooms/bookings/<int:booking_id>/approve/', hod_views.approve_classroom_booking, name='approve_classroom_booking'),
    path('admin/classrooms/schedule/', hod_views.classroom_schedule, name='classroom_schedule'),
    path('admin/classrooms/maintenance/', hod_views.classroom_maintenance, name='classroom_maintenance'),
    path('admin/classrooms/maintenance/report/', hod_views.report_maintenance, name='report_maintenance'),
    
    # ============================================================================
    # NEW ECAP FEATURES - STAFF URLs
    # ============================================================================
    
    # Online Examination
    path('staff/online_exams/', staff_views.staff_my_online_exams, name='staff_my_online_exams'),
    path('staff/online_exams/create/', staff_views.staff_create_online_exam, name='staff_create_online_exam'),
    
    # Research
    path('staff/research/', staff_views.staff_my_research, name='staff_my_research'),
    path('staff/research/add/', staff_views.staff_add_research, name='staff_add_research'),
    
    # Gate Pass Approvals
    path('staff/gate_pass/approvals/', staff_views.staff_gate_pass_approvals, name='staff_gate_pass_approvals'),
    
    # ============================================================================
    # NEW ECAP FEATURES - STUDENT URLs
    # ============================================================================
    
    # Online Exams
    path('student/online_exams/', student_views.student_online_exams, name='student_online_exams'),
    path('student/online_exams/results/', student_views.student_exam_results, name='student_exam_results'),
    
    # Certificates
    path('student/certificates/', student_views.student_my_certificates, name='student_my_certificates'),
    path('student/certificates/request/', student_views.student_request_certificate, name='student_request_certificate'),
    
    # Internships
    path('student/internships/', student_views.student_my_internships, name='student_my_internships'),
    path('student/internships/add/', student_views.student_add_internship, name='student_add_internship'),
    
    # Medical
    path('student/medical/', student_views.student_medical_records, name='student_medical_records'),
    
    # Gate Pass
    path('student/gate_pass/', student_views.student_gate_pass, name='student_gate_pass'),
    path('student/gate_pass/my/', student_views.student_my_gate_passes, name='student_my_gate_passes'),
    
    # Sports & Activities
    path('student/activities/', student_views.student_sports_activities, name='student_sports_activities'),
    path('student/activities/my/', student_views.student_my_activities, name='student_my_activities'),
    
    # Anti-Ragging
    path('student/ragging/report/', student_views.student_report_ragging, name='student_report_ragging'),
    
    # ============================================================================
    # REAL-TIME CHAT SYSTEM URLs
    # ============================================================================
    
    # Main Chat Interface
    path('chat/', chat_views.chat_interface, name='chat_interface'),
    path('chat/room/<int:room_id>/', chat_views.chat_room, name='chat_room'),
    path('chat/start/<int:user_id>/', chat_views.start_private_chat, name='start_private_chat'),
    
    # AJAX Endpoints
    path('chat/rooms/', chat_views.get_chat_rooms, name='get_chat_rooms'),
    path('chat/room/<int:room_id>/messages/', chat_views.get_chat_messages, name='get_chat_messages'),
    path('chat/send/', chat_views.send_chat_message, name='send_chat_message'),
    path('chat/upload/', chat_views.upload_chat_file, name='upload_chat_file'),
    path('chat/read/', chat_views.mark_messages_read, name='mark_messages_read'),
    path('chat/search/', chat_views.search_messages, name='search_messages'),
    path('chat/online-users/', chat_views.get_online_users, name='get_online_users'),
    path('chat/notifications/', chat_views.chat_notifications, name='chat_notifications'),
    
    # Room Management
    path('chat/room/create/', chat_views.create_chat_room, name='create_chat_room'),
    path('chat/room/<int:room_id>/add-participants/', chat_views.add_room_participants, name='add_room_participants'),
    
    # ============================================================================
    # PLACEMENT & CAREER PORTAL URLs
    # ============================================================================
    
    # HOD/Admin Placement Management
    path('admin/placement/dashboard/', placement_views.placement_dashboard, name='placement_dashboard'),
    path('admin/placement/companies/', placement_views.manage_companies, name='manage_companies'),
    path('admin/placement/company/add/', placement_views.add_company, name='add_company'),
    path('admin/placement/company/<int:company_id>/edit/', placement_views.edit_company, name='edit_company'),
    path('admin/placement/drives/', placement_views.manage_placement_drives, name='manage_placement_drives'),
    path('admin/placement/drive/add/', placement_views.add_placement_drive, name='add_placement_drive'),
    path('admin/placement/drive/<int:drive_id>/edit/', placement_views.edit_placement_drive, name='edit_placement_drive'),
    path('admin/placement/drive/<int:drive_id>/', placement_views.view_placement_drive, name='view_placement_drive'),
    path('admin/placement/drive/<int:drive_id>/rounds/', placement_views.manage_interview_rounds, name='manage_interview_rounds'),
    path('admin/placement/drive/<int:drive_id>/round/add/', placement_views.add_interview_round, name='add_interview_round'),
    path('admin/placement/round/<int:round_id>/slots/', placement_views.manage_interview_slots, name='manage_interview_slots'),
    path('admin/placement/round/<int:round_id>/slots/bulk/', placement_views.create_bulk_slots, name='create_bulk_slots'),
    path('admin/placement/analytics/', placement_views.placement_analytics, name='placement_analytics'),
    
    # Student Placement Portal
    path('student/placement/', placement_views.student_placement_dashboard, name='student_placement_dashboard'),
    path('student/placement/profile/', placement_views.student_placement_profile, name='student_placement_profile'),
    path('student/placement/apply/<int:drive_id>/', placement_views.apply_placement, name='apply_placement'),
    path('student/placement/application/<int:application_id>/', placement_views.view_application_status, name='view_application_status'),
    path('student/placement/interview/<int:round_id>/book/', placement_views.book_interview_slot, name='book_interview_slot'),
    
    # AJAX Endpoints
    path('placement/application/status/update/', placement_views.update_application_status, name='update_application_status'),
    path('placement/offer/respond/', placement_views.respond_to_offer, name='respond_to_offer'),
    
    # ============================================================================
    # LEARNING MANAGEMENT SYSTEM (LMS) URLs
    # ============================================================================
    
    # HOD/Admin LMS Management
    path('admin/lms/dashboard/', lms_views.lms_dashboard, name='lms_dashboard'),
    path('admin/lms/modules/', lms_views.manage_course_modules, name='manage_course_modules'),
    path('admin/lms/module/add/', lms_views.add_course_module, name='add_course_module'),
    path('admin/lms/module/<int:module_id>/edit/', lms_views.edit_course_module, name='edit_course_module'),
    path('admin/lms/quizzes/', lms_views.manage_quizzes, name='manage_quizzes'),
    path('admin/lms/module/<int:module_id>/quiz/add/', lms_views.add_quiz, name='add_quiz'),
    path('admin/lms/quiz/<int:quiz_id>/questions/', lms_views.manage_quiz_questions, name='manage_quiz_questions'),
    path('admin/lms/quiz/<int:quiz_id>/question/add/', lms_views.add_quiz_question, name='add_quiz_question'),
    path('admin/lms/question/<int:question_id>/options/', lms_views.manage_question_options, name='manage_question_options'),
    path('admin/lms/assignments/', lms_views.manage_assignments, name='manage_assignments'),
    path('admin/lms/assignment/add/', lms_views.add_assignment, name='add_assignment'),
    path('admin/lms/assignment/<int:assignment_id>/submissions/', lms_views.view_assignment_submissions, name='view_assignment_submissions'),
    path('admin/lms/submission/<int:submission_id>/grade/', lms_views.grade_assignment, name='grade_assignment'),
    path('admin/lms/enrollments/', lms_views.manage_course_enrollments, name='manage_course_enrollments'),
    path('admin/lms/enrollments/bulk/', lms_views.bulk_enroll_students, name='bulk_enroll_students'),
    
    # Staff LMS Views
    path('staff/lms/dashboard/', lms_views.staff_lms_dashboard, name='staff_lms_dashboard'),
    path('staff/lms/modules/', lms_views.staff_view_modules, name='staff_view_modules'),
    path('staff/lms/assignments/', lms_views.staff_view_assignments, name='staff_view_assignments'),
    
    # Student LMS Views
    path('student/lms/dashboard/', lms_views.student_lms_dashboard, name='student_lms_dashboard'),
    path('student/lms/course/<int:course_id>/modules/', lms_views.student_view_course_modules, name='student_view_course_modules'),
    path('student/lms/module/<int:module_id>/', lms_views.student_view_module, name='student_view_module'),
    path('student/lms/quiz/<int:quiz_id>/take/', lms_views.student_take_quiz, name='student_take_quiz'),
    path('student/lms/quiz/attempt/<int:attempt_id>/result/', lms_views.student_quiz_result, name='student_quiz_result'),
    path('student/lms/assignments/', lms_views.student_view_assignments, name='student_view_assignments'),
    path('student/lms/assignment/<int:assignment_id>/submit/', lms_views.student_submit_assignment, name='student_submit_assignment'),
    
    # LMS AJAX Endpoints
    path('lms/module/complete/', lms_views.mark_module_complete, name='mark_module_complete'),
    path('lms/module/bookmark/', lms_views.toggle_bookmark, name='toggle_bookmark'),
    
    # Analytics URLs
    path("analytics/", analytics_views.analytics_dashboard, name='analytics_dashboard'),
    path("analytics/attendance/", analytics_views.attendance_analytics, name='attendance_analytics'),
    path("analytics/academic-performance/", analytics_views.academic_performance_analytics, name='academic_performance_analytics'),
    path("analytics/financial/", analytics_views.financial_analytics, name='financial_analytics'),
    path("analytics/report-builder/", analytics_views.custom_report_builder, name='custom_report_builder'),
    path("analytics/reports/", analytics_views.report_builder, name='report_builder'),  # Alias for navigation
    path("analytics/export/", analytics_views.export_report, name='export_report'),
    
    # API URLs
    path("api/", include('main_app.api_urls')),
    
    # Performance Monitoring URLs
    path("performance/", performance_views.performance_dashboard, name='performance_dashboard'),
    path("performance/api/", performance_views.performance_api, name='performance_api'),
    path("performance/clear-cache/", performance_views.clear_cache, name='clear_cache'),
    path("performance/optimize-static/", performance_views.optimize_static, name='optimize_static'),
    path("performance/slow-queries/", performance_views.slow_queries, name='slow_queries'),
    path("performance/error-logs/", performance_views.error_logs, name='error_logs'),
    path("performance/system-resources/", performance_views.system_resources, name='system_resources'),
    path("performance/export-data/", performance_views.export_performance_data, name='export_performance_data'),
    path("performance/database-analysis/", performance_views.database_analysis, name='database_analysis'),
    path("performance/cache-analysis/", performance_views.cache_analysis, name='cache_analysis'),
    path("performance/recommendations/", performance_views.optimization_recommendations, name='optimization_recommendations'),
    
    # Public Links Management URLs
    path("manage-public-links/", hod_views.manage_public_links, name='manage_public_links'),
    path("add-public-link/", hod_views.add_public_link, name='add_public_link'),
    path("edit-public-link/<int:link_id>/", hod_views.edit_public_link, name='edit_public_link'),
    path("delete-public-link/<int:link_id>/", hod_views.delete_public_link, name='delete_public_link'),
    path("toggle-link-status/<int:link_id>/", hod_views.toggle_link_status, name='toggle_link_status'),
    path("reorder-public-links/", hod_views.reorder_public_links, name='reorder_public_links'),
    
    # Comprehensive HOD Dashboard URLs
    path("hod-dashboard/", hod_views.hod_comprehensive_dashboard, name='hod_comprehensive_dashboard'),
    path("user-management-hub/", hod_views.user_management_hub, name='user_management_hub'),
    path("bulk-student-upload/", hod_views.bulk_student_upload, name='bulk_student_upload'),
    path("academic-operations/", hod_views.academic_operations, name='academic_operations'),
    path("reports-hub/", hod_views.reports_hub, name='reports_hub'),
    
    # Timetable Management URLs
    path("timetable-dashboard/", hod_views.timetable_dashboard, name='timetable_dashboard'),
    path("create-timetable/", hod_views.create_timetable, name='create_timetable'),
    path("edit-timetable/<int:timetable_id>/", hod_views.edit_timetable, name='edit_timetable'),
    path("delete-timetable/<int:timetable_id>/", hod_views.delete_timetable, name='delete_timetable'),
    path("view-timetable/<int:timetable_id>/", hod_views.view_timetable, name='view_timetable'),
    path("auto-schedule/", hod_views.auto_schedule, name='auto_schedule'),
    path("check-conflicts/", hod_views.check_conflicts, name='check_conflicts'),
    path("timetable-export/<int:timetable_id>/<str:format>/", hod_views.timetable_export, name='timetable_export'),
    path("faculty-availability/<int:faculty_id>/", hod_views.faculty_availability, name='faculty_availability'),
    path("classroom-availability/<int:classroom_id>/<str:date>/", hod_views.classroom_availability, name='classroom_availability'),
    path("timetable-statistics/", hod_views.timetable_statistics, name='timetable_statistics'),
    path("check-timetable-conflicts/", hod_views.check_timetable_conflicts, name='check_timetable_conflicts'),
    
    # Department Management URLs
    path("department-analytics/", hod_views.department_analytics, name='department_analytics'),
    path("department-management/", hod_views.department_management, name='department_management'),
    path("add-department/", hod_views.add_department, name='add_department'),
    path("edit-department/<int:department_id>/", hod_views.edit_department, name='edit_department'),
    path("delete-department/<int:department_id>/", hod_views.delete_department, name='delete_department'),
    path("add-program/", hod_views.add_program, name='add_program'),
    path("edit-program/<int:program_id>/", hod_views.edit_program, name='edit_program'),
    path("delete-program/<int:program_id>/", hod_views.delete_program, name='delete_program'),
    path("department-performance/<int:department_id>/", hod_views.department_performance, name='department_performance'),
    path("department-export/<int:department_id>/<str:format>/", hod_views.department_export, name='department_export'),
    path("department-statistics-api/", hod_views.department_statistics_api, name='department_statistics_api'),
    path("department-analytics-api/", hod_views.department_analytics_api, name='department_analytics_api'),
    path("department-comparison/", hod_views.department_comparison, name='department_comparison'),
    
    # Approval Center URLs
    path("approval-center/", hod_views.approval_center, name='approval_center'),
    path("student-leave-approvals/", hod_views.student_leave_approvals, name='student_leave_approvals'),
    path("staff-leave-approvals/", hod_views.staff_leave_approvals, name='staff_leave_approvals'),
    path("approve-leave/<int:leave_id>/<str:leave_type>/", hod_views.approve_leave, name='approve_leave'),
    path("reject-leave/<int:leave_id>/<str:leave_type>/", hod_views.reject_leave, name='reject_leave'),
    path("bulk-approve-leaves/", hod_views.bulk_approve_leaves, name='bulk_approve_leaves'),
    path("classroom-booking-approvals/", hod_views.classroom_booking_approvals, name='classroom_booking_approvals'),
    path("approve-classroom-booking/<int:booking_id>/", hod_views.approve_classroom_booking, name='approve_classroom_booking'),
    path("reject-classroom-booking/<int:booking_id>/", hod_views.reject_classroom_booking, name='reject_classroom_booking'),
    path("approval-statistics/", hod_views.approval_statistics, name='approval_statistics'),
    path("approval-timeline/", hod_views.approval_timeline, name='approval_timeline'),
    
    # Gemini AI Integration URLs
    path("ai/insights/enhanced/", gemini_views.ai_student_insights_enhanced, name='ai_student_insights_enhanced'),
    path("ai/chatbot/api/", gemini_views.ai_chatbot_api, name='ai_chatbot_api'),
    path("ai/chatbot/", gemini_views.ai_chatbot_interface, name='ai_chatbot'),
    path("ai/generate-content/", gemini_views.ai_generate_study_material, name='ai_generate_content'),
    path("ai/compose-email/", gemini_views.ai_compose_email, name='ai_compose_email'),
    path("ai/generate-questions/", gemini_views.ai_generate_questions, name='ai_generate_questions'),
    path("ai/career-counseling/", gemini_views.ai_career_counseling, name='ai_career_counseling'),
]
