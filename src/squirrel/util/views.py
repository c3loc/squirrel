""" Utility functions that we need in many places
"""

from django.shortcuts import get_object_or_404, redirect, render, reverse


def get_form(request, model, form, instance_id, form_initial=None):
    """ Shows the form with the provided instance
    """

    # If no instance is specified, use an empty form
    if not instance_id:
        form_instance = form(initial=form_initial)

    # If it is specified, get the instance and fill the form
    else:
        model_instance = get_object_or_404(model, id=instance_id)
        form_instance = form(instance=model_instance)

    return render(request, "instance.html", {"form": form_instance})


def post_form(request, model, form, instance_id=None, next_page="orders:orders"):
    """ Saves the form in the request if valid and redirects to the account overview.
        Shows the form again if it is invalid
    """

    # Get the instance of our object. If there is none, a new instance is created
    if instance_id:
        instance = get_object_or_404(model, id=instance_id)
    else:
        instance = None

    form_instance = form(request.POST, instance=instance)
    if form_instance.is_valid():
        form_instance.save()

        return redirect(reverse(next_page))

    return render(request, "instance.html", {"form": form_instance})
