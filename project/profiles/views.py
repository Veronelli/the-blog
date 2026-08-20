from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from profiles.forms import PublicProfileForm
from profiles.models import (
    PublicProfile,
    SocialNetworkConfig,
    SocialNetworkInstance,
    VariableInstance,
)


def _value_form_key(identifier: str) -> str:
    return f"value_{identifier}"


@login_required
def dashboard_profile(request: HttpRequest) -> HttpResponse:
    profile = getattr(request.user, "public_profile", None)
    if request.method == "POST":
        form = PublicProfileForm(request.POST, instance=profile)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.user = request.user
            saved.save()
            return redirect("profiles:dashboard")
    else:
        initial = None
        if profile is None:
            initial = {
                "public_username": request.user.username,
                "first_name": request.user.first_name or "",
                "last_name": request.user.last_name or "",
            }
        form = PublicProfileForm(instance=profile, initial=initial)
    instances = SocialNetworkInstance.objects.filter(author=request.user)
    return render(
        request,
        "profiles/dashboard_profile.html",
        {"form": form, "profile": profile, "instances": instances},
    )


@login_required
def dashboard_instance_create(request: HttpRequest) -> HttpResponse:
    configs = SocialNetworkConfig.objects.all()
    if request.method == "POST":
        config = get_object_or_404(
            SocialNetworkConfig, pk=request.POST.get("config")
        )
        with transaction.atomic():
            instance = SocialNetworkInstance.objects.create(
                author=request.user, config=config
            )
            for variable in config.variables.all():
                value = request.POST.get(_value_form_key(variable.identifier), "")
                if not value:
                    continue
                try:
                    VariableInstance.objects.create(
                        social_network_instance=instance,
                        variable=variable,
                        value=value,
                    ).full_clean()
                except ValidationError:
                    instance.delete()
                    raise
        return redirect("profiles:dashboard")
    return render(
        request,
        "profiles/dashboard_instance_create.html",
        {"configs": configs},
    )


@login_required
def dashboard_instance_edit(
    request: HttpRequest, pk: int
) -> HttpResponse:
    instance = get_object_or_404(
        SocialNetworkInstance, pk=pk, author=request.user
    )
    if request.method == "POST":
        for variable_instance in instance.variable_instances.filter(archived=False):
            key = _value_form_key(variable_instance.variable.identifier)
            if key in request.POST:
                variable_instance.value = request.POST[key]
                variable_instance.save()
        return redirect("profiles:dashboard")
    return render(
        request,
        "profiles/dashboard_instance_edit.html",
        {"instance": instance},
    )


@login_required
def dashboard_instance_archive(
    request: HttpRequest, pk: int
) -> HttpResponse:
    if request.method == "POST":
        instance = get_object_or_404(
            SocialNetworkInstance, pk=pk, author=request.user
        )
        instance.archive()
    return redirect("profiles:dashboard")