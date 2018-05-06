# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from operator import itemgetter

from django.db.models import Count
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from snacksdb.models import Ballot, Nomination
from snacksdb.utils import get_snack_source, SnackSourceException


@method_decorator(login_required, name='dispatch')
class Vote(generic.TemplateView):
    template_name = 'snacksdb/vote.html'

    def post(self, request, *pos, **kw):
        if (settings.VOTES_PER_MONTH -
                    Ballot.objects.this_month().filter(user=request.user).count() < 1):
            return HttpResponseForbidden(_("Nice try! You're out of votes for the month!"))

        if 'snack_id' not in request.POST:
            return HttpResponseBadRequest(_('POST data must contain "snack_id".'))
        if 'snack_name' not in request.POST:
            return HttpResponseBadRequest(_('POST data must contain "snack_name".'))

        Ballot.objects.create(snack_id=request.POST['snack_id'], user=request.user)

        messages.success(request, _("Got it! You voted for {snack_name}.").format(
            snack_name=request.POST['snack_name']
        ))

        return redirect('snacksdb:vote')

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)

        user_votes = Ballot.objects.this_month().filter(user=self.request.user)

        mandatory_snacks, optional_snacks = self.fetch_snacks()
        optional_snacks = self.postprocess_optional_snacks(optional_snacks, user_votes)

        context['mandatory_snacks'] = mandatory_snacks
        context['optional_snacks'] = optional_snacks
        context['votes_remaining'] = max(0, settings.VOTES_PER_MONTH - user_votes.count())
        context['nominations_remaining'] = Nomination.remaining_in_month(self.request.user)

        return context

    def fetch_snacks(self):
        """
        Return a 2-tuple of snack lists: (mandatory_snacks, optional_snacks)
        as determined by the Snack Food API.
        """
        try:
            snack_list = get_snack_source().list()
        except SnackSourceException as sse:
            messages.error(self.request, sse.msg)
            return [], []

        mandatory_snacks = [s for s in snack_list if not s['optional']]
        optional_snacks = [s for s in snack_list if s['optional']]

        return mandatory_snacks, optional_snacks

    def postprocess_optional_snacks(self, optional_snacks, user_votes):
        """
        Does three things:
        1) Filter out snacks that haven't been suggested yet this month.
        2) Annotate each snack with the total number of votes it's received this month.
        3) Indicate which snacks the user has voted for this month.
        """
        new_optional_snacks = []

        # Get a list of snack IDs the user has voted for this month.
        voted_snack_ids = {v.snack_id for v in user_votes}

        # Count total votes for each snack ID.
        votes_by_snack = self.count_votes_by_snack()

        for snack in self.filter_unnominated_snacks(optional_snacks):  # (1)
            snack['total_votes'] = votes_by_snack.get(snack['id'], 0)  # (2)
            snack['received_vote'] = snack['id'] in voted_snack_ids  # (3)
            new_optional_snacks.append(snack)

        return sorted(new_optional_snacks, key=itemgetter('total_votes'), reverse=True)

    def filter_unnominated_snacks(self, snacks):
        """
        Filter out snacks that haven't been suggested yet this month.
        """
        return [
            s for s in snacks
            if s['id'] in Nomination.objects.this_month().values_list('snack_id', flat=True)
        ]

    def count_votes_by_snack(self):
        """
        Count the total number of votes for each snack
        See the docs for more information about aggregation using QuerySets:
        https://docs.djangoproject.com/en/2.0/topics/db/aggregation/
        """
        votes_by_snack = Ballot.objects.this_month().values('snack_id')
        return {
            item['snack_id']: item['total']
            for item in votes_by_snack.annotate(total=Count('snack_id'))
        }
