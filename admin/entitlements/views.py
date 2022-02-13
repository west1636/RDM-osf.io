from __future__ import unicode_literals

import logging
from urllib.parse import urlencode

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, View

from osf.models import Institution
from osf.models import InstitutionEntitlement

logger = logging.getLogger(__name__)


class InstitutionEntitlementList(ListView):
    paginate_by = 25
    template_name = 'entitlements/list.html'
    permission_required = 'osf.admin_institution_entitlement'
    raise_exception = True
    model = InstitutionEntitlement
    institutions = Institution.objects.all().order_by('name')
    selected_id = institutions.first().id

    def get_queryset(self):
        return InstitutionEntitlement.objects.order_by('entitlement')

    def get_context_data(self, **kwargs):
        institution_id = int(self.kwargs.get('institution_id', self.request.GET.get('institution_id', self.selected_id)))
        object_list = self.object_list.filter(institution_id=institution_id)

        page_size = self.get_paginate_by(object_list)
        paginator, page, query_set, is_paginated = self.paginate_queryset(object_list, page_size)

        kwargs.setdefault('institutions', self.institutions)
        kwargs.setdefault('institution_id', institution_id)
        kwargs.setdefault('selected_id', institution_id)
        kwargs.setdefault('entitlements', query_set)
        kwargs.setdefault('page', page)

        return super(InstitutionEntitlementList, self).get_context_data(**kwargs)


class BulkAddInstitutionEntitlement(PermissionRequiredMixin, View):
    permission_required = 'osf.admin_institution_entitlement'
    raise_exception = True

    def post(self, request):
        institution_id = request.POST.get('institution_id')
        entitlements = request.POST.getlist('entitlements')
        login_availability_list = request.POST.getlist('login_availability')

        for idx, entitlement in enumerate(entitlements):
            InstitutionEntitlement.objects.create(institution_id=institution_id,
                                                  entitlement=entitlement,
                                                  login_availability=login_availability_list[idx] == 'on',
                                                  modifier=request.user)

        base_url = reverse('institutions:entitlements')
        query_string = urlencode({'institution_id': institution_id})
        return redirect('{}?{}'.format(base_url, query_string))


class ToggleInstitutionEntitlement(PermissionRequiredMixin, View):
    permission_required = 'osf.admin_institution_entitlement'
    raise_exception = True

    def post(self, request, *args, **kwargs):
        entitlement = InstitutionEntitlement.objects.get(id=self.kwargs['entitlement_id'])
        entitlement.login_availability = not entitlement.login_availability
        entitlement.modifier = request.user
        entitlement.save()

        base_url = reverse('institutions:entitlements')
        query_string = urlencode({'institution_id': self.kwargs['institution_id']})
        return redirect('{}?{}'.format(base_url, query_string))


class DeleteInstitutionEntitlement(PermissionRequiredMixin, View):
    permission_required = 'osf.admin_institution_entitlement'
    raise_exception = True

    def post(self, request, *args, **kwargs):
        entitlement = InstitutionEntitlement.objects.get(id=self.kwargs['entitlement_id'])
        entitlement.delete()

        base_url = reverse('institutions:entitlements')
        query_string = urlencode({'institution_id': self.kwargs['institution_id']})
        return redirect('{}?{}'.format(base_url, query_string))
