from django.test import TestCase
from mystery.models import Interest
from mystery.tests.utils import mock_req, random_user
from mystery import views
from mock import patch
from django.contrib.auth import get_user_model
from core.models import OrgGroup, OfficeLocation
from django.core.urlresolvers import reverse

class MatchTest(TestCase):

    fixtures = ['core-test-fixtures', ]

    def test_pending_match_default_page(self):
        """ Verify pending match is default page after submission """
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_COFFEE,
                                                      'departments':[org.pk],
                                                      'locations':[office.pk]})
        self.assertEqual(Interest.objects.count(), 1)
        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_pending_must_be_logged_in(self):
        """ A user must be logged in to view pending match page """
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        self.client.post(reverse('mystery:mystery'), {'meet_choice':Interest.CHOICE_COFFEE,
                                                      'departments':[org.pk],
                                                      'locations':[office.pk]})
        self.client.logout()
        resp = self.client.get(reverse('mystery:mystery'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp['Location'])

    def test_cancel_pending_match(self):
        """ Test cancellation before match is complete """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission = Interest()
        submission.owner = user1
        submission.for_coffee = True
        submission.save()
        submission.locations.add(office)
        submission.departments.add(org)

        self.assertEqual(submission.is_active, True)
        resp = self.client.get(reverse('mystery:close_cancel', args=(submission.id,)))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('mystery:mystery'), resp['Location'])
        self.assertEqual(Interest.objects.get(id=submission.id).is_active, False)

    def test_assigned_match(self):
        """ Test a valid match results in assigned match page """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_coffee = True
        submission2.locations.add(office)
        submission2.departments.add(org)
        submission2.is_active = True
        submission2.save()

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, reverse("mystery:close_incomplete", args=(submission1.id,)))
        self.assertContains(resp, reverse("mystery:close_complete", args=(submission1.id,)))

        # verify assigned match page requires login
        self.client.logout()
        resp = self.client.get(reverse('mystery:mystery'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp['Location'])

    def test_assigned_video_match(self):
        """ Test a valid video match results in assigned match page """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.video_chat = True
        submission1.save()
        submission1.departments.add(org)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.video_chat = True
        submission2.departments.add(org)
        submission2.is_active = True
        submission2.save()

        self.assertEqual(submission2.is_active, True)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Success", status_code=200)

    def test_cancel_assigned_match(self):
        """ Test cancellation of assigned match """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_coffee = True
        submission2.locations.add(office)
        submission2.departments.add(org)
        submission2.is_active = True
        submission2.save()

        resp = self.client.get(reverse('mystery:close_incomplete', args=(submission1.id,)))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('forms', resp['Location'])
        self.assertEqual(Interest.objects.get(id=submission1.id).is_active, False)
        self.assertEqual(Interest.objects.get(id=submission2.id).is_active, True)

    def test_complete_assigned_match(self):
        """ Test closure of assigned match """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_coffee = True
        submission2.locations.add(office)
        submission2.departments.add(org)
        submission2.is_active = True
        submission2.save()

        resp = self.client.get(reverse('mystery:close_complete', args=(submission1.id,)))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('forms', resp['Location'])
        self.assertEqual(Interest.objects.get(id=submission1.id).is_active, False)
        self.assertEqual(Interest.objects.get(id=submission2.id).is_active, True)

    def test_non_matching_type(self):
        """ Verify registrations with different meet type (lunch, etc) do not register as a match. """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_lunch = True
        submission2.locations.add(office)
        submission2.departments.add(org)
        submission2.is_active = True
        submission2.save()

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_non_matching_org(self):
        """ Verify registrations with different org do not register as a match. """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

        user2 = random_user()
        org2 = OrgGroup()
        org2.parent = org
        org2.title = "test org"
        org2.save()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_coffee = True
        submission2.locations.add(office)
        submission2.departments.add(org2)
        submission2.is_active = True
        submission2.save()

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_non_matching_location(self):
        """ Verify registrations with different location do not register as a match. """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

        user2 = random_user()
        office2 = OfficeLocation()
        office2.id = "test_id"
        office2.street = "test office"
        office2.city = "test office"
        office2.state = "test office"
        office2.zip = "test office"
        office2.save()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_coffee = True
        submission2.locations.add(office2)
        submission2.departments.add(org)
        submission2.is_active = True
        submission2.save()

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_non_matching_active(self):
        """ Verify registrations with different location do not register as a match. """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office = OfficeLocation.objects.all()[0]
        org = OrgGroup.objects.filter(parent__isnull=True)[0]

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.save()
        submission1.locations.add(office)
        submission1.departments.add(org)

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.is_active = False
        submission2.save()
        submission2.for_coffee = True
        submission2.locations.add(office)
        submission2.departments.add(org)
        submission2.save()

        resp = self.client.get(reverse('mystery:mystery'))
        self.assertContains(resp, "Cancel this", status_code=200)

    def test_interest_save(self):
        """ Test interest initial_save function """
        user1 = get_user_model().objects.get(username='test1@example.com')
        self.client.login(username='test1@example.com', password='1')

        office_list = OfficeLocation.objects.all()
        org_list = OrgGroup.objects.filter(parent__isnull=True)

        submission1 = Interest()
        submission1.owner = user1
        submission1.for_coffee = True
        submission1.initial_save(locations=office_list, departments=org_list)

        self.assertNotEqual(submission1.id, None)
        self.assertEqual(submission1.locations.count(), len(office_list))
        self.assertEqual(submission1.departments.count(), len(org_list))
        self.assertEqual(submission1.match, None)

        user2 = random_user()
        submission2 = Interest()
        submission2.owner = user2
        submission2.for_coffee = True
        submission2.save()
        submission2.locations.add(office_list[0])
        submission2.departments.add(org_list[0])
        submission2.save()


        self.assertNotEqual(submission2.id, None)
        self.assertEqual(submission2.locations.count(), 1)
        self.assertEqual(submission2.departments.count(), 1)
        self.assertEqual(submission2.match, submission1)
        submission1 = Interest.objects.get(id=submission1.id)  # refresh
        self.assertEqual(submission1.match, submission2)
