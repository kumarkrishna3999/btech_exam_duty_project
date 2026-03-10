from django.db import models


# ---------------- FACULTY ----------------

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ---------------- LAB TECH ----------------

class LabTech(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ---------------- ROOM ----------------

class Room(models.Model):
    room_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.room_number


# ---------------- COURSE ----------------

class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ---------------- SEMESTER ----------------

class Semester(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return f"Sem {self.number}"


# ---------------- SUBJECT ----------------

class Subject(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.course} Sem {self.semester.number} – {self.code} – {self.name}"
# ---------------- SHIFT ----------------

class Shift(models.Model):

    SHIFT_CHOICES = [
        ("Morning", "Morning"),
        ("Evening", "Evening"),
    ]

    exam_date = models.DateField()

    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_CHOICES
    )

    subjects = models.ManyToManyField(Subject)

    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.exam_date} - {self.shift_type}"

# ---------------- DUTY ----------------

class Duty(models.Model):

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    invigilator1 = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inv1",
    )

    invigilator2_faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inv2_faculty",
    )

    invigilator2_labtech = models.ForeignKey(
        LabTech,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inv2_labtech",
    )

    def __str__(self):
        return f"{self.shift} - {self.room}"