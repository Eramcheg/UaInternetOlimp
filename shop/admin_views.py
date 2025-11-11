from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from shop.models import Group, Olympiad, OlympiadTask, LibraryType, Material
from shop.forms import GroupForm, OlympiadForm, TaskFormSet, MaterialForm
from shop.views import is_admin


@login_required
@user_passes_test(is_admin)
def group_list(request):
    groups = Group.objects.all()
    return render(request, "admin_tools/AT_group_list.html", {"groups": groups})

@login_required
@user_passes_test(is_admin)
def library_list(request):
    libraries = LibraryType.objects.all()
    return render(request, "admin_tools/AT_library_list.html", {"libraries": libraries})


@login_required
@user_passes_test(is_admin)
def group_edit(request, pk=None):
    obj = Group.objects.get(pk=pk) if pk else None
    form = GroupForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Групу збережено")
        return redirect("admin_tools", feature_name="group_list")
    return render(request, "admin_tools/AT_group_edit.html", {"form": form, "obj": obj})


@login_required
@user_passes_test(is_admin)
def group_delete(request, pk):
    obj = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        title = obj.title
        obj.delete()
        messages.success(request, f"Групу «{title}» видалено.")
        return redirect("admin_tools", feature_name="group_list")
    return render(request, "admin_tools/AT_confirm_delete.html",
                  {"obj": obj, "back_url": reverse("admin_tools", args=["group_list"])})


@login_required
@user_passes_test(is_admin)
def olymp_list(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    olymps = (
        group.olympiads
        .all()
        .order_by('-year', 'name')
        .prefetch_related(Prefetch('tasks', queryset=OlympiadTask.objects.order_by('order', 'title')))
    )
    return render(request, "admin_tools/AT_olymp_list.html", {"group": group, "olymps": olymps})


@login_required
@user_passes_test(is_admin)
def materials_list(request, library_id):
    library = get_object_or_404(LibraryType, pk=library_id)
    materials = (
        library.materials
        .all()
        .order_by('title')
    )
    return render(request, "admin_tools/AT_materials_list.html", {"library": library, "materials": materials})


@login_required
@user_passes_test(is_admin)
def olymp_edit(request, group_id, pk=None):
    group = get_object_or_404(Group, pk=group_id)
    olymp = Olympiad.objects.filter(group=group, pk=pk).first()

    form = OlympiadForm(request.POST or None, instance=olymp)
    # ✅ ensure unique check sees group
    form.instance.group = group

    formset = TaskFormSet(request.POST or None, request.FILES or None, instance=olymp)

    if request.method == "POST":
        if form.is_valid():
            olymp = form.save(commit=False)  # already has group set
            olymp.save()

            # Rebind formset to the saved parent if this was a new one
            if pk is None:
                formset = TaskFormSet(request.POST, request.FILES, instance=olymp)

            if formset.is_valid():
                formset.save()
                messages.success(request, "Олімпіада та задачі збережені.")
                return redirect("olymps_admin:olymp_list", group_id=group.id)
        # If not valid, form will now show a proper “already exists” error
    return render(
        request,
        "admin_tools/AT_olymp_edit.html",
        {"form": form, "formset": formset, "group": group, "obj": olymp},
    )


@login_required
@user_passes_test(is_admin)
def materials_edit(request, library_id, pk=None):
    library = get_object_or_404(LibraryType, pk=library_id)
    materials = Material.objects.filter(library=library, pk=pk).first()

    form = MaterialForm(request.POST or None, request.FILES, instance=materials)
    # ✅ ensure unique check sees group
    form.instance.library = library

    if request.method == "POST":
        if form.is_valid():
            materials = form.save(commit=False)  # already has group set
            materials.save()
            # Rebind formset to the saved parent if this was a new one
            messages.success(request, "Олімпіада та задачі збережені.")
            return redirect("olymps_admin:material_list", library_id=library.id)
        # If not valid, form will now show a proper “already exists” error
    else:
        # ВАЖНО: на GET — только instance, без data/files
        form = MaterialForm(instance=materials)
        form.instance.library = library

    return render(
        request,
        "admin_tools/AT_material_edit.html",
        {"form": form, "library": library, "obj": materials},
    )


@login_required
@user_passes_test(is_admin)
def olymp_delete(request, group_id, pk):
    group = get_object_or_404(Group, pk=group_id)
    obj = get_object_or_404(Olympiad, pk=pk, group=group)
    if request.method == "POST":
        name = str(obj)
        obj.delete()
        messages.success(request, f"«{name}» видалено.")
        return redirect("admin_tools", feature_name="group_list")
    return render(request, "admin_tools/AT_confirm_delete.html",
                  {"obj": obj, "back_url": reverse("admin_tools", args=["group_list"])})
