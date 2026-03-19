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

# ---------------- Helper to safely register models ----------------
def safe_register(model, admin_class=None):
    try:
        if admin_class:
            admin.site.register(model, admin_class)
        else:
            admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

# ---------------- DUTY GENERATOR (RANDOM LABTECH ANYWHERE) ----------------
def generate_duties(shift):
    rooms = list(Room.objects.filter(is_active=True).order_by("room_number"))
    faculty = list(Faculty.objects.filter(is_active=True))
    labtechs = list(LabTech.objects.filter(is_active=True))

    if not rooms or len(faculty) < 2:
        print("Not enough faculty")
        return

    random.shuffle(faculty)
    random.shuffle(labtechs)
    random.shuffle(rooms)

    Duty.objects.filter(shift=shift).delete()

    duties = []
    used_faculty = set()
    used_labtechs = set()
    faculty_index = 0
    labtech_index = 0

    print(f"Starting: {len(rooms)} rooms, {len(faculty)} faculty, {len(labtechs)} labtechs")

    for room in rooms:
        # INV1: Always Faculty (unique)
        inv1 = None
        attempts = 0
        while inv1 is None and attempts < len(faculty) * 2:
            candidate = faculty[faculty_index % len(faculty)]
            if candidate not in used_faculty:
                inv1 = candidate
                used_faculty.add(candidate)
                break
            faculty_index += 1
            attempts += 1
        
        if inv1 is None:
            print(f"No faculty left for {room.room_number}")
            continue

        # INV2: 50% RANDOM LabTech (ANY room) or Faculty
        inv2 = None
        inv2_is_labtech = False
        
        if labtechs and random.random() < 0.5:
            attempts = 0
            while inv2 is None and attempts < len(labtechs) * 2:
                candidate = labtechs[labtech_index % len(labtechs)]
                if candidate not in used_labtechs:
                    inv2 = candidate
                    used_labtechs.add(candidate)
                    inv2_is_labtech = True
                    break
                labtech_index += 1
                attempts += 1

        if inv2 is None:
            attempts = 0
            while inv2 is None and attempts < len(faculty) * 2:
                candidate = faculty[faculty_index % len(faculty)]
                if candidate not in used_faculty and candidate != inv1:
                    inv2 = candidate
                    used_faculty.add(candidate)
                    inv2_is_labtech = False
                    break
                faculty_index += 1
                attempts += 1

        if inv2 is None:
            print(f"No inv2 for {room.room_number}")
            continue

        if inv2_is_labtech:
            duty = Duty(
                shift=shift,
                room=room,
                invigilator1=inv1,
                invigilator2_labtech=inv2
            )
            print(f"{room.room_number}: {inv1.name} + LABTECH {inv2.name}")
        else:
            duty = Duty(
                shift=shift,
                room=room,
                invigilator1=inv1,
                invigilator2_faculty=inv2
            )
            print(f"{room.room_number}: {inv1.name} + FACULTY {inv2.name}")
        
        duties.append(duty)

    if duties:
        Duty.objects.bulk_create(duties)
        print(f"SUCCESS: {len(duties)}/{len(rooms)} duties created!")
        print(f"Faculty used: {len(used_faculty)} unique")
        print(f"LabTech used: {len(used_labtechs)} unique")
    else:
        print("No duties created!")

# ---------------- SHIFT ADMIN ----------------
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "exam_date",
        "shift_type",
        "subject_list",
        "view_chart_button",
        "shuffle_button",
        "lock_button",
        "faculty_used",
        "labtech_used",
    )
    filter_horizontal = ("subjects",)

    def subject_list(self, obj):
        return ", ".join([s.name for s in obj.subjects.all()])
    subject_list.short_description = "Subjects"

    def faculty_used(self, obj):
        duties = Duty.objects.filter(shift=obj)
        faculty = set()
        for duty in duties:
            if duty.invigilator1:
                faculty.add(duty.invigilator1.name)
            if duty.invigilator2_faculty:
                faculty.add(duty.invigilator2_faculty.name)
        return f"{len(faculty)} faculty"
    faculty_used.short_description = "Faculty Used"

    def labtech_used(self, obj):
        duties = Duty.objects.filter(shift=obj)
        labtechs = set()
        for duty in duties:
            if duty.invigilator2_labtech:
                labtechs.add(duty.invigilator2_labtech.name)
        return f"{len(labtechs)} labtechs"
    labtech_used.short_description = "Labtechs Used"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("view-chart/<int:shift_id>/", self.admin_site.admin_view(self.view_chart)),
            path("shuffle/<int:shift_id>/", self.admin_site.admin_view(self.shuffle_shift)),
            path("lock/<int:shift_id>/", self.admin_site.admin_view(self.lock_shift)),
        ]
        return custom_urls + urls

    def view_chart(self, request, shift_id):
        shift = get_object_or_404(Shift, pk=shift_id)
        if not shift.is_locked:
            generate_duties(shift)
        duties = Duty.objects.filter(shift=shift).order_by("room__room_number")
        return render(request, "duty/duty_chart.html", {"shift": shift, "duties": duties})

    def shuffle_shift(self, request, shift_id):
        shift = get_object_or_404(Shift, pk=shift_id)
        if shift.is_locked:
            messages.error(request, "Shift is locked. Unlock to shuffle.")
            return redirect("/admin/duty/shift/")
        generate_duties(shift)
        messages.success(request, "Duties shuffled successfully with random labtech assignment!")
        return redirect(f"/admin/duty/shift/view-chart/{shift_id}/")

    def lock_shift(self, request, shift_id):
        shift = get_object_or_404(Shift, pk=shift_id)
        shift.is_locked = not shift.is_locked
        shift.save()
        status = "locked" if shift.is_locked else "unlocked"
        messages.success(request, f"Shift {status} successfully!")
        return redirect("/admin/duty/shift/")

    def view_chart_button(self, obj):
        return format_html('<a class="button" href="/admin/duty/shift/view-chart/{}/">View</a>', obj.id)

    def shuffle_button(self, obj):
        if obj.is_locked:
            return "Locked"
        return format_html('<a class="button" href="/admin/duty/shift/shuffle/{}/">Shuffle</a>', obj.id)

    def lock_button(self, obj):
        label = "Unlock" if obj.is_locked else "Lock"
        return format_html('<a class="button" href="/admin/duty/shift/lock/{}/">{}</a>', obj.id, label)

# ---------------- OTHER ADMINS ----------------
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)

class LabTechAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)

class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "is_active")
    list_editable = ("is_active",)
    search_fields = ("room_number",)

class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)

class SemesterAdmin(admin.ModelAdmin):
    list_display = ("number",)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "course", "semester")
    list_filter = ("course", "semester")
    search_fields = ("name", "code")

# ---------------- REGISTER MODELS ----------------
safe_register(Shift, ShiftAdmin)
safe_register(Faculty, FacultyAdmin)
safe_register(LabTech, LabTechAdmin)
safe_register(Room, RoomAdmin)
safe_register(Course, CourseAdmin)
safe_register(Semester, SemesterAdmin)
safe_register(Subject, SubjectAdmin)
safe_register(Duty)