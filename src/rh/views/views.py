import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.http import FileResponse, HttpResponseForbidden, JsonResponse

from project_reports.models import ProjectMonthlyReport as Report
from django.shortcuts import get_object_or_404, render

from ..models import (
    ActivityDomain,
    Cluster,
    DisaggregationLocation,
    Location,
    TargetLocation,
)

RECORDS_PER_PAGE = 10


def landing_page(request):
    users_count = User.objects.all().count()
    locations_count = Location.objects.all().count()
    reports_count = Report.objects.all().count()

    context = {
        "users": users_count,
        "locations": locations_count,
        "reports": reports_count,
    }

    return render(request, "landing.html", context)


@login_required
def download_user_guide(request):
    document_path = os.path.join(settings.MEDIA_ROOT, "documents", "ReportHub-User-Guide.pdf")

    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You do not have permission to access this resource.")

    # Open the file in binary mode
    response = FileResponse(open(document_path, "rb"))

    return response


#############################################
#               Project Views
#############################################


def copy_target_location_disaggregation_locations(location, disaggregation_location):
    """Copy Disaggregation Locations"""
    try:
        # Duplicate the original disaggregation location by retrieving it with the provided primary key.
        new_disaggregation_location = get_object_or_404(DisaggregationLocation, pk=disaggregation_location.pk)
        new_disaggregation_location.pk = None  # Generate a new primary key for the duplicated location.
        new_disaggregation_location.save()  # Save the duplicated location to the database.

        # Associate the duplicated disaggregation location with the new target location.
        new_disaggregation_location.target_location = location

        # Save the changes made to the duplicated disaggregation location.
        new_disaggregation_location.save()

        # Return True to indicate that the copy operation was successful.
        return True
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


@login_required
def load_activity_domains(request):
    cluster_ids = [int(i) for i in request.POST.getlist("clusters[]") if i]

    # Define a Prefetch object to optimize the related activitydomain_set
    prefetch_activitydomain = Prefetch(
        "activitydomain_set",
        queryset=ActivityDomain.objects.order_by("name"),
    )

    clusters = Cluster.objects.filter(pk__in=cluster_ids).prefetch_related(prefetch_activitydomain)

    clusters = [
        {
            "label": cluster.title,
            "choices": [{"value": domain.pk, "label": domain.name} for domain in cluster.activitydomain_set.all()],
        }
        for cluster in clusters
    ]

    return JsonResponse(clusters, safe=False)


def copy_project_target_location(plan, location):
    """Copy Target Locations"""
    try:
        # Duplicate the original target location
        # by retrieving it with the provided primary key.
        new_location = get_object_or_404(TargetLocation, pk=location.pk)
        new_location.pk = None  # Generate a new primary key for the duplicated location.
        new_location.save()  # Save the duplicated location to the database.

        # Associate the duplicated location with the new activity plan.
        new_location.activity_plan = plan
        new_location.project = plan.project

        # Set the location as active and in a draft state to indicate it's a copy.
        new_location.active = True
        new_location.state = "draft"

        # Save the changes made to the duplicated location.
        new_location.save()

        # Return the duplicated location.
        return new_location
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


@login_required
def load_facility_sites(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist("clusters[]") if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids)

    response = "".join(
        [
            f'<optgroup label="{cluster.title}">'
            + "".join(
                [
                    f'<option value="{facility.pk}">{facility}</option>'
                    for facility in cluster.facilitysitetype_set.order_by("name")
                ]
            )
            + "</optgroup>"
            for cluster in clusters
        ]
    )

    return JsonResponse(response, safe=False)
