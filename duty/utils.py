import random
from .models import Duty, Faculty, LabTech, Room, Shift

def auto_assign_duties(shift_id):
    shift = Shift.objects.get(id=shift_id)
    rooms = Room.objects.all()
    faculties = list(Faculty.objects.filter(is_active=True))
    labtechs = list(LabTech.objects.filter(is_active=True))

    random.shuffle(faculties)
    random.shuffle(labtechs)

    faculty_index = 0
    lab_index = 0

    for room in rooms:
        duty, created = Duty.objects.get_or_create(room=room, shift=shift)
        if duty.locked:
            continue

        if shift.name.lower() == "morning" and lab_index < len(labtechs):
            duty.labtech = labtechs[lab_index]
            lab_index += 1
            if faculty_index < len(faculties):
                duty.faculty = faculties[faculty_index]
                faculty_index += 1
        else:
            if faculty_index < len(faculties):
                duty.faculty = faculties[faculty_index]
                faculty_index += 1
            if faculty_index < len(faculties):
                duty.backup_faculty = faculties[faculty_index]
                faculty_index += 1

        duty.save()