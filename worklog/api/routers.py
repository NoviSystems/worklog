from rest_framework import routers
from worklog import models


class WorkItemRouter(routers.DefaultRouter):

	def get_default_base_name(self, viewset):

		try:
			date = self.kwargs['date']
			self.queryset = models.WorkItem.objects.filter(date=date)
		except KeyError:
			self.queryset = models.WorkItem.objects.all()

		return super(WorkItemRouter, self).get_default_base_name(viewset)
