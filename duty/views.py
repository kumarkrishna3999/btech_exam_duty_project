from django.shortcuts import get_object_or_404, redirect
from .models import Shift, Duty
import random
from django.http import HttpResponse

def shuffle_duty(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    if shift.locked:
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))

    duties = list(Duty.objects.filter(shift=shift))
    random.shuffle(duties)

    # Optional: reorder duties
    for idx, duty in enumerate(duties):
        duty.order = idx
        duty.save()

    return redirect(request.META.get('HTTP_REFERER', '/admin/'))

def toggle_shift_lock(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    shift.locked = not shift.locked
    shift.save()
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))

def home(request):
    return HttpResponse("Exam Duty System Running Successfully")