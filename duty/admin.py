from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html
import random

from .models import (
    Shift,
    Duty,
    Faculty,
    LabTech,
    Room,
    Course,
    Semester,
    Subject
)


# ---------------- DUTY GENERATOR ----------------

def generate_duties(shift):

    rooms = list(Room.objects.filter(is_active=True).order_by("room_number"))
    faculty = list(Faculty.objects.filter(is_active=True))
    labtechs = list(LabTech.objects.filter(is_active=True))

    if not rooms or len(faculty) < 2:
        print("Not enough faculty")
        return

    random.shuffle(faculty)
    random.shuffle(labtechs)

    Duty.objects.filter(shift=shift).delete()

    duties = []

    faculty_index = 0
    lab_index = 0

    for room in rooms:

        inv1 = faculty[faculty_index % len(faculty)]
        faculty_index += 1

        if labtechs and random.choice([True, False]):

            inv2 = labtechs[lab_index % len(labtechs)]
            lab_index += 1

            duties.append(
                Duty(
                    shift=shift,
                    room=room,
                    invigilator1=inv1,
                    invigilator2_labtech=inv2
                )
            )

        else:

            inv2 = faculty[faculty_index % len(faculty)]
            faculty_index += 1

            duties.append(
                Duty(
                    shift=shift,
                    room=room,
                    invigilator1=inv1,
                    invigilator2_faculty=inv2
                )
            )

    Duty.objects.bulk_create(duties)


# ---------------- SHIFT ADMIN ----------------

class ShiftAdmin(admin.ModelAdmin):

    list_display = (
        "exam_date",
        "shift_type",
        "subject_list",
        "view_chart_button",
        "shuffle_button",
        "lock_button",
    )

    filter_horizontal = ("subjects",)

    def subject_list(self, obj):
        return ", ".join([s.name for s in obj.subjects.all()])
    subject_list.short_description = "Subjects"

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "view-chart/<int:shift_id>/",
                self.admin_site.admin_view(self.view_chart),
            ),
            path(
                "shuffle/<int:shift_id>/",
                self.admin_site.admin_view(self.shuffle_shift),
            ),
            path(
                "lock/<int:shift_id>/",
                self.admin_site.admin_view(self.lock_shift),
            ),
        ]

        return custom_urls + urls

    # ---------- VIEW CHART ----------

    def view_chart(self, request, shift_id):

        shift = get_object_or_404(Shift, pk=shift_id)

        if not shift.is_locked:
            generate_duties(shift)

        duties = Duty.objects.filter(shift=shift).order_by("room__room_number")

        return render(
            request,
            "duty/duty_chart.html",
            {
                "shift": shift,
                "duties": duties,
            },
        )

    # ---------- SHUFFLE ----------

    def shuffle_shift(self, request, shift_id):

        shift = get_object_or_404(Shift, pk=shift_id)

        if shift.is_locked:
            messages.error(request, "Shift is locked. Unlock to shuffle.")
            return redirect("/admin/duty/shift/")

        generate_duties(shift)

        messages.success(request, "Duties shuffled successfully!")

        return redirect(f"/admin/duty/shift/view-chart/{shift_id}/")

    # ---------- LOCK ----------

    def lock_shift(self, request, shift_id):

        shift = get_object_or_404(Shift, pk=shift_id)

        shift.is_locked = not shift.is_locked
        shift.save()

        return redirect("/admin/duty/shift/")

    # ---------- BUTTONS ----------

    def view_chart_button(self, obj):
        return format_html(
            '<a class="button" href="/admin/duty/shift/view-chart/{}/">View</a>',
            obj.id,
        )

    def shuffle_button(self, obj):

        if obj.is_locked:
            return "Locked"

        return format_html(
            '<a class="button" href="/admin/duty/shift/shuffle/{}/">Shuffle</a>',
            obj.id,
        )

    def lock_button(self, obj):

        label = "Unlock" if obj.is_locked else "Lock"

        return format_html(
            '<a class="button" href="/admin/duty/shift/lock/{}/">{}</a>',
            obj.id,
            label,
        )


# ---------------- FACULTY ADMIN ----------------

class FacultyAdmin(admin.ModelAdmin):

    list_display = ("name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)


# ---------------- LABTECH ADMIN ----------------

class LabTechAdmin(admin.ModelAdmin):

    list_display = ("name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)


# ---------------- ROOM ADMIN ----------------

class RoomAdmin(admin.ModelAdmin):

    list_display = ("room_number", "is_active")
    list_editable = ("is_active",)
    search_fields = ("room_number",)


# ---------------- COURSE ADMIN ----------------

class CourseAdmin(admin.ModelAdmin):

    list_display = ("name",)


# ---------------- SEMESTER ADMIN ----------------

class SemesterAdmin(admin.ModelAdmin):

    list_display = ("number",)


# ---------------- SUBJECT ADMIN ----------------

class SubjectAdmin(admin.ModelAdmin):

    list_display = ("name", "code", "course", "semester")
    list_filter = ("course", "semester")
    search_fields = ("name", "code")
# ---------------- REGISTER MODELS ----------------

admin.site.register(Shift, ShiftAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(LabTech, LabTechAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)