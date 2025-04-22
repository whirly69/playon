from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Structure
from .forms import StructureForm

@login_required
def structure_dashboard(request):
    structures = Structure.objects.filter(created_by=request.user).order_by('name')
    structure_forms = {}

    if request.method == 'POST' and 'name' in request.POST:
        form = StructureForm(request.POST)
        if form.is_valid():
            structure = form.save(commit=False)
            structure.created_by = request.user
            structure.save()
            return redirect('structure_dashboard')
    else:
        form = StructureForm()

    for structure in structures:
        structure_forms[structure.id] = StructureForm(instance=structure)

    return render(request, 'facilities/structure_dashboard.html', {
        'structures': structures,
        'form': form,
        'structure_forms': structure_forms,
    })

@login_required
def structure_update(request, structure_id):
    structure = get_object_or_404(Structure, id=structure_id, created_by=request.user)
    if request.method == 'POST':
        form = StructureForm(request.POST, instance=structure)
        if form.is_valid():
            form.save()
    return redirect('structure_dashboard')

@login_required
def structure_delete(request, structure_id):
    structure = get_object_or_404(Structure, id=structure_id, created_by=request.user)
    if request.method == 'POST':
        structure.delete()
    return redirect('structure_dashboard')