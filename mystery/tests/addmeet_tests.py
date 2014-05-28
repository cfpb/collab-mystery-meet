from django.test import TestCase
from django.core.urlresolvers import reverse
from core.models import OrgGroup, OfficeLocation
from mystery.models import Interest

class AddMeetTest(TestCase):

    fixtures = ['core-test-fixtures', ]

    def test_add_meet_view(self):
        """ Verify appropriate divisions, locations """
        self.client.login(username='test1@example.com', password='1')
        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "I'd like to meet for", status_code=200)

        # verify only root org groups are listed
        good_org = OrgGroup.objects.filter(parent__isnull=True)[0]
        bad_org = OrgGroup.objects.filter(parent__isnull=False)[0]
        self.assertContains(resp, good_org.title)
        self.assertNotContains(resp, bad_org.title)

        # Verify office locations are listed
        office = OfficeLocation.objects.all()[0]
        self.assertContains(resp, office.name)

    def test_submit_meet(self):
        """ Test a valid POST submission to add a meet. """
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        resp = self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_COFFEE,
                                                             'departments':[org.pk],
                                                             'locations':[office.pk]})
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_bad_meet(self):
        """ Test an incomplete POST submission to add a meet. """
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        resp = self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_COFFEE,
                                                             'departments':[org.pk],
                                                             'locations':[]})
        self.assertContains(resp, 'like to meet for')

        resp = self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_COFFEE,
                                                             'departments':[],
                                                             'locations':[office.pk]})
        self.assertContains(resp, 'like to meet for')

        resp = self.client.post(reverse('mystery:mystery'), {'departments':[org.pk],
                                                             'locations':[office.pk]})
        self.assertContains(resp, 'like to meet for')

    def test_video_meet(self):
        """ Test a video POST submission to add a meet. """
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        resp = self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_VIDEO,
                                                             'departments':[],
                                                             'locations':[]})
        self.assertContains(resp, 'like to meet for')

        resp = self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_VIDEO,
                                                             'departments':[org.pk],
                                                             'locations':[]})
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_must_be_logged_in(self):
        """ A user must be logged in to create a meet. """
        resp = self.client.get(reverse('mystery:mystery'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp['Location'])
