import calendar
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_control

from rh.models import Indicator, Location, Project

from .forms import (
    ActivityPlanReportForm,
    DisaggregationReportFormSet,
    ProjectMonthlyReportForm,
    TargetLocationReportFormSet,
)
from .models import ActivityPlanReport, ProjectMonthlyReport


@cache_control(no_store=True)
@login_required
def index_project_report_view(request, project):
    """Project Monthly Report View"""
    project = get_object_or_404(Project, pk=project)
    project_reports = ProjectMonthlyReport.objects.all()
    project_reports_todo = project_reports.filter(state__in=["todo", "pending"])
    project_report_complete = project_reports.filter(state="complete")
    project_state = project.state
    parent_page = {
        "in-progress": "active_projects",
        "draft": "draft_projects",
        "done": "completed_projects",
        "archive": "archived_projects",
    }.get(project_state, None)
    context = {
        "project": project,
        "parent_page": parent_page,
        "project_reports": project_reports,
        "project_reports_todo": project_reports_todo,
        "project_report_complete": project_report_complete,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/views/monthly_reports_view_base.html", context)


@cache_control(no_store=True)
@login_required
def create_project_monthly_report_view(request, project):
    """View for creating a project."""
    project = get_object_or_404(Project, pk=project)

    # Get the current date
    current_date = datetime.now()

    # Calculate the last day of the current month
    last_day = calendar.monthrange(current_date.year, current_date.month)[1]

    # Create a new date representing the end of the current month
    end_of_month = datetime(current_date.year, current_date.month, last_day)

    form = ProjectMonthlyReportForm(
        request.POST or None,
        initial={"report_due_date": end_of_month, "project": project},
    )

    project_state = project.state
    parent_page = {
        "in-progress": "active_projects",
        "draft": "draft_projects",
        "done": "completed_projects",
        "archive": "archived_projects",
    }.get(project_state, None)

    if request.method == "POST":
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.save()
            return redirect(
                "create_project_monthly_report_progress",
                project=project.pk,
                report=report.pk,
            )

    context = {
        "project": project,
        "report_form": form,
        "parent_page": parent_page,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }
    return render(request, "project_reports/forms/monthly_report_form.html", context)


@cache_control(no_store=True)
@login_required
def details_monthly_progress_view(request, project, report):
    """Project Monthly Report Read View"""
    project = get_object_or_404(Project, pk=project)
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    activity_reports = monthly_report.activityplanreport_set.select_related("activity_plan", "indicator")

    project_state = project.state
    parent_page = {
        "in-progress": "active_projects",
        "draft": "draft_projects",
        "done": "completed_projects",
        "archive": "archived_projects",
    }.get(project_state, None)
    context = {
        "project": project,
        "monthly_report": monthly_report,
        "activity_reports": activity_reports,
        "parent_page": parent_page,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/views/monthly_report_view.html", context)


def get_project_and_report_details(project_id, report_id=None):
    project = get_object_or_404(Project, pk=project_id)
    project_state = project.state
    activity_plans = project.activityplan_set.select_related("activity_domain", "activity_type", "activity_detail")
    target_locations = project.targetlocation_set.select_related("province", "district", "zone").all()
    monthly_report_instance = None

    if report_id is not None:
        monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report_id)

    return (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    )


def get_target_locations_doamin(target_locations):
    # TODO: use cache
    # Create Q objects for each location type
    province_q = Q(id__in=[location.province.id for location in target_locations if location.province])
    district_q = Q(id__in=[location.district.id for location in target_locations if location.district])
    zone_q = Q(id__in=[location.zone.id for location in target_locations if location.zone])

    # Collect provinces, districts, and zones using a single query for each
    target_location_provinces = Location.objects.filter(province_q)
    target_location_districts = Location.objects.filter(district_q)
    target_location_zones = Location.objects.filter(zone_q)

    return (target_location_provinces, target_location_districts, target_location_zones)


@cache_control(no_store=True)
@login_required
def create_project_monthly_report_progress_view(request, project, report):
    """Create View"""
    (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    ) = get_project_and_report_details(project, report)

    (
        target_location_provinces,
        target_location_districts,
        target_location_zones,
    ) = get_target_locations_doamin(target_locations)

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=len(activity_plans),
        can_delete=True,
    )

    activity_report_formset = ActivityReportFormset(
        request.POST or None,
        instance=monthly_report_instance,
    )

    location_report_formsets = []
    for activity_report in activity_report_formset:
        # Create a target location formset for each activity plan form
        location_report_formset = TargetLocationReportFormSet(
            request.POST or None,
            instance=activity_report.instance,
            prefix=f"locations_report_{activity_report.prefix}",
        )
        for location_report_form in location_report_formset.forms:
            # Create a disaggregation formset for each target location form
            disaggregation_report_formset = DisaggregationReportFormSet(
                request.POST or None,
                instance=location_report_form.instance,
                prefix=f"disaggregation_report_{location_report_form.prefix}",
            )
            location_report_form.disaggregation_report_formset = disaggregation_report_formset

        # Loop through the forms in the formset and set queryset values for specific fields
        if not request.POST:
            for i, form in enumerate(location_report_formset.forms):
                if i < len(target_locations):
                    form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
                    form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
                    form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)

        location_report_formsets.append(location_report_formset)

    # Loop through the forms in the formset and set initial and queryset values for specific fields
    if not request.POST:
        for i, form in enumerate(activity_report_formset.forms):
            if i < len(activity_plans):
                activity_plan = activity_plans[i]
                if not form.instance.pk:
                    form.initial = {
                        "activity_plan": activity_plan,
                        "project_id": project,
                    }
                form.fields["indicator"].queryset = activity_plan.indicators.all()

    if request.method == "POST":
        if activity_report_formset.is_valid():
            for activity_report_form in activity_report_formset:
                indicator_data = activity_report_form.cleaned_data.get("indicator")
                if indicator_data:
                    activity_report = activity_report_form.save(commit=False)
                    activity_report.monthly_report = monthly_report_instance
                    activity_report.save()

                    # Process target location forms and their disaggregation forms
                    for location_report_formset in location_report_formsets:
                        if location_report_formset.instance == activity_report:
                            if location_report_formset.is_valid():
                                for location_report_form in location_report_formset:
                                    cleaned_data = location_report_form.cleaned_data
                                    province = cleaned_data.get("province")
                                    district = cleaned_data.get("district")

                                    if province and district:
                                        location_report_instance = location_report_form.save(commit=False)
                                        location_report_instance.activity_plan_report = activity_report
                                        location_report_instance.save()

                                    if hasattr(
                                        location_report_form,
                                        "disaggregation_report_formset",
                                    ):
                                        disaggregation_report_formset = (
                                            location_report_form.disaggregation_report_formset.forms
                                        )

                                        # Delete the exisiting instances of the disaggregation location
                                        # reports and create new
                                        # based on the indicator disaggregations
                                        new_report_disaggregations = []
                                        for disaggregation_report_form in disaggregation_report_formset:
                                            if disaggregation_report_form.is_valid():
                                                if (
                                                    disaggregation_report_form.cleaned_data != {}
                                                    and disaggregation_report_form.cleaned_data.get("target") > 0
                                                ):
                                                    disaggregation_report_instance = disaggregation_report_form.save(
                                                        commit=False
                                                    )
                                                    disaggregation_report_instance.target_location = (
                                                        location_report_instance
                                                    )
                                                    disaggregation_report_instance.save()
                                                    new_report_disaggregations.append(disaggregation_report_instance.id)

                                        all_report_disaggregations = (
                                            location_report_form.instance.disaggregationlocationreport_set.all()
                                        )
                                        for disaggregation_report in all_report_disaggregations:
                                            if disaggregation_report.id not in new_report_disaggregations:
                                                disaggregation_report.delete()

            # activity_report_formset.save()
            return redirect(
                "view_monthly_report",
                project=project.pk,
                report=monthly_report_instance.pk,
            )
        else:
            # TODO:
            # Handle invalid activity_plan_formset
            # Add error handling code here
            pass

    parent_page = {
        "in-progress": "active_projects",
        "draft": "draft_projects",
        "done": "completed_projects",
        "archive": "archived_projects",
    }.get(project_state, None)

    combined_formset = zip(activity_report_formset.forms, location_report_formsets)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "activity_plans": activity_plans,
        "report_form": monthly_report_instance,
        "activity_report_formset": activity_report_formset,
        # 'location_report_formset': location_report_formset,
        "combined_formset": combined_formset,
        "parent_page": parent_page,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/forms/monthly_report_progress_form.html", context)


@cache_control(no_store=True)
@login_required
def update_project_monthly_report_progress_view(request, project, report):
    """Update View"""
    (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    ) = get_project_and_report_details(project, report)

    (
        target_location_provinces,
        target_location_districts,
        target_location_zones,
    ) = get_target_locations_doamin(target_locations)

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=0,
        can_delete=True,
    )

    activity_report_formset = ActivityReportFormset(
        request.POST or None,
        instance=monthly_report_instance,
    )

    location_report_formsets = []
    for activity_report in activity_report_formset:
        # Create a target location formset for each activity plan form
        location_report_formset = TargetLocationReportFormSet(
            request.POST or None,
            instance=activity_report.instance,
            prefix=f"locations_report_{activity_report.prefix}",
        )
        for location_report_form in location_report_formset.forms:
            # Create a disaggregation formset for each target location form
            disaggregation_report_formset = DisaggregationReportFormSet(
                request.POST or None,
                instance=location_report_form.instance,
                prefix=f"disaggregation_report_{location_report_form.prefix}",
            )
            location_report_form.disaggregation_report_formset = disaggregation_report_formset

        # Loop through the forms in the formset and set queryset values for specific fields
        if not request.POST:
            for i, form in enumerate(location_report_formset.forms):
                if i < len(target_locations):
                    form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
                    form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
                    form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)

        location_report_formsets.append(location_report_formset)

    # Loop through the forms in the formset and set initial and queryset values for specific fields
    if not request.POST:
        for i, form in enumerate(activity_report_formset.forms):
            if i < len(activity_plans):
                activity_plan = activity_plans[i]
                form.fields["indicator"].queryset = activity_plan.indicators.all()

    if request.method == "POST":
        if activity_report_formset.is_valid():
            for activity_report_form in activity_report_formset:
                indicator_data = activity_report_form.cleaned_data.get("indicator")
                if indicator_data:
                    activity_report = activity_report_form.save(commit=False)
                    activity_report.monthly_report = monthly_report_instance
                    activity_report.save()

                    # Process target location forms and their disaggregation forms
                    for location_report_formset in location_report_formsets:
                        if location_report_formset.instance == activity_report:
                            if location_report_formset.is_valid():
                                for location_report_form in location_report_formset:
                                    cleaned_data = location_report_form.cleaned_data
                                    province = cleaned_data.get("province")
                                    district = cleaned_data.get("district")

                                    if province and district:
                                        location_report_instance = location_report_form.save(commit=False)
                                        location_report_instance.activity_plan_report = activity_report
                                        location_report_instance.save()

                                    if hasattr(
                                        location_report_form,
                                        "disaggregation_report_formset",
                                    ):
                                        disaggregation_report_formset = (
                                            location_report_form.disaggregation_report_formset.forms
                                        )

                                        # Delete the exisiting instances of the disaggregation
                                        # location reports and create new
                                        # based on the indicator disaggregations
                                        new_report_disaggregations = []
                                        for disaggregation_report_form in disaggregation_report_formset:
                                            if disaggregation_report_form.is_valid():
                                                if (
                                                    disaggregation_report_form.cleaned_data != {}
                                                    and disaggregation_report_form.cleaned_data.get("target") > 0
                                                ):
                                                    disaggregation_report_instance = disaggregation_report_form.save(
                                                        commit=False
                                                    )
                                                    disaggregation_report_instance.target_location = (
                                                        location_report_instance
                                                    )
                                                    disaggregation_report_instance.save()
                                                    new_report_disaggregations.append(disaggregation_report_instance.id)

                                        all_report_disaggregations = (
                                            location_report_form.instance.disaggregationlocationreport_set.all()
                                        )
                                        for disaggregation_report in all_report_disaggregations:
                                            if disaggregation_report.id not in new_report_disaggregations:
                                                disaggregation_report.delete()

            return redirect(
                "view_monthly_report",
                project=project.pk,
                report=monthly_report_instance.pk,
            )
        else:
            # TODO:
            # Handle invalid activity_plan_report_formset
            # Add error handling code here
            pass

    parent_page = {
        "in-progress": "active_projects",
        "draft": "draft_projects",
        "done": "completed_projects",
        "archive": "archived_projects",
    }.get(project_state, None)

    combined_formset = zip(activity_report_formset.forms, location_report_formsets)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "activity_plans": activity_plans,
        "report_form": monthly_report_instance,
        "activity_report_formset": activity_report_formset,
        "combined_formset": combined_formset,
        "parent_page": parent_page,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/forms/monthly_report_progress_form.html", context)


@login_required
def get_location_report_empty_form(request):
    """Get an empty location Report form for a project"""
    # Get the project object based on the provided project ID
    project = get_object_or_404(Project, pk=request.POST.get("project"))

    # Get all existing target locaitions for the project
    target_locations = project.targetlocation_set.select_related("province", "district", "zone").all()

    (
        target_location_provinces,
        target_location_districts,
        target_location_zones,
    ) = get_target_locations_doamin(target_locations)

    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        can_delete=True,
    )

    # Create an instance of ActivityPlanFormSet using the project instance and form_kwargs
    activity_report_formset = ActivityReportFormset()

    # Get the prefix index from the request
    prefix_index = request.POST.get("prefix_index")

    # Create an instance of TargetLocationFormSet with a prefixed name
    location_report_formset = TargetLocationReportFormSet(
        prefix=f"locations_report_{activity_report_formset.prefix}-{prefix_index}"
    )

    # for target_location_form in target_location_formset.forms:
    # Create a disaggregation formset for each target location form
    location_report_form = location_report_formset.empty_form

    location_report_form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
    location_report_form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
    location_report_form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)

    disaggregation_report_formset = DisaggregationReportFormSet(
        request.POST or None,
        instance=location_report_form.instance,
        prefix=f"disaggregation_report_{location_report_form.prefix}",
    )
    location_report_form.disaggregation_report_formset = disaggregation_report_formset

    # Prepare context for rendering the target location form template
    context = {
        "location_report_form": location_report_form,
    }

    # Render the target location form template and generate HTML
    html = render_to_string("project_reports/forms/location_report_empty_form.html", context)

    # Return JSON response containing the generated HTML
    return JsonResponse({"html": html})


@login_required
def get_disaggregations_report_empty_forms(request):
    """Get target location empty form"""

    # Create a dictionary to hold disaggregation forms per location prefix
    location_disaggregation_report_dict = {}
    if request.POST.get("indicator"):
        # Get selected indicators
        indicator = get_object_or_404(Indicator, pk=int(request.POST.get("indicator")))

        # Get selected locations prefixes
        locations_report_prefix = request.POST.getlist("locations_prefixes[]")

        # Loop through each Indicator and retrieve its related Disaggregations
        related_disaggregations = indicator.disaggregation_set.all()

        initial_data = []

        # Populate initial data with related disaggregations
        if related_disaggregations:
            for disaggregation in related_disaggregations:
                initial_data.append({"disaggregation": disaggregation})

            # Create DisaggregationFormSet for each location prefix
            for location_report_prefix in locations_report_prefix:
                DisaggregationReportFormSet.extra = len(related_disaggregations)
                disaggregation_report_formset = DisaggregationReportFormSet(
                    prefix=f"disaggregation_report_{location_report_prefix}",
                    initial=initial_data,
                )

                # Generate HTML for each disaggregation form and store in dictionary
                for disaggregation_report_form in disaggregation_report_formset.forms:
                    context = {
                        "disaggregation_report_form": disaggregation_report_form,
                    }
                    html = render_to_string(
                        "project_reports/forms/disaggregation_report_empty_form.html",
                        context,
                    )

                    if location_report_prefix in location_disaggregation_report_dict:
                        location_disaggregation_report_dict[location_report_prefix].append(html)
                    else:
                        location_disaggregation_report_dict.update({location_report_prefix: [html]})

        # Set back extra to 0 to avoid empty forms if refreshed.
        DisaggregationReportFormSet.extra = 0

    # Return JSON response containing generated HTML forms
    return JsonResponse(location_disaggregation_report_dict)