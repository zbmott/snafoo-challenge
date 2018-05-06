# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from snacksdb import forms
from snacksdb.models import Nomination
from snacksdb.utils import get_snack_source, SnackSourceException


class Nominate(FormView):
    FormView = FormView  # Preserve reference for mocking during tests.
    DELIMITER = '--DELIM--'

    form_class = forms.NominationForm
    template_name = 'snacksdb/nominate.html'

    def dispatch(self, request, *pos, **kw):
        """
        Check to see if the user is allowed to place a nomination before rendering
        the page. If they're not, send them back to the Vote view.
        """
        if Nomination.remaining_in_month(request.user) < 1:
            msg = _("Sorry, you don't have any nominations left. Try again next month!")
            messages.warning(request, msg)
            return redirect('snacksdb:vote')

        return super().dispatch(request, *pos, **kw)

    def post(self, request, *pos, **kw):
        if request.POST.get('snack_id'):
            snack_id, snack_name = request.POST['snack_id'].split(self.DELIMITER)
            return self.finalize_nomination(snack_id, snack_name)

        return super().post(request, *pos, **kw)

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)

        context['nominations_remaining'] = Nomination.remaining_in_month(self.request.user)
        context['unnominated_snacks'] = self.get_unnominated_snacks()
        context['delimiter'] = self.DELIMITER

        return context

    def get_unnominated_snacks(self):
        """
        Return a list of all the snacks that have not yet been nominated this month.
        """
        try:
            optional_snacks = [s for s in get_snack_source().list() if s['optional']]
        except SnackSourceException as sse:
            messages.error(self.request, sse.msg)
            return []

        this_month = Nomination.objects.this_month()
        nominated_snacks = this_month.values_list('snack_id', flat=True).distinct()

        return [s for s in optional_snacks if s['id'] not in nominated_snacks]

    def form_valid(self, form):
        """
        Local validation was successful. Submit the snack nomination to the Source.
        """
        try:
            snack_info = get_snack_source().suggest(**form.cleaned_data)
        except SnackSourceException as sse:
            messages.error(self.request, sse.msg)
            return self.form_invalid(form)  # Preserve the user's input.

        return self.finalize_nomination(snack_info['id'], snack_info['name'])

    def finalize_nomination(self, snack_id, snack_name):
        """
        Create a Nomination instance and redirect the user back to the voting page.
        """
        # Record the nomination locally.
        Nomination.objects.create(snack_id=snack_id, user=self.request.user)

        msg = _("Thanks for nominating {snack_name}! Great suggestion!")
        messages.success(self.request, msg.format(snack_name=snack_name))

        return redirect('snacksdb:vote')

