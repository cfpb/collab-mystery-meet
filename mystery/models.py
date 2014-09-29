from django.db import models
from collab.settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from core.models import OfficeLocation, OrgGroup
from django.db.models import Q


class Interest(models.Model):
    CHOICE_LUNCH = "lunch"
    CHOICE_COFFEE = "coffee"
    CHOICE_VIDEO = "video"

    owner = models.ForeignKey(AUTH_USER_MODEL)
    is_active = models.BooleanField(default=True)
    match = models.ForeignKey('self', null=True)
    for_lunch = models.BooleanField(default=False)
    for_coffee = models.BooleanField(default=False)
    video_chat = models.BooleanField(default=False)
    locations = models.ManyToManyField(OfficeLocation)
    departments = models.ManyToManyField(OrgGroup)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.owner.username

    def initial_save(self, locations=None, departments=None):
        super(Interest, self).save()
        if locations:
            self.locations.add(*locations)
        if departments:
            self.departments.add(*departments)
        if self.is_active and not self.match:
            self.add_match_if_exists()

    def save(self, *args, **kwargs):
        super(Interest, self).save(*args, **kwargs)
        if self.is_active and not self.match:
            self.add_match_if_exists()

    def add_match_if_exists(self):
        interests = self.find_matching_interests()
        if interests.count() > 0:
            # TODO investigate locking
            existing_interest = interests[0]
            existing_interest.match = self
            existing_interest.save()
            self.match = existing_interest
            self.save()

    def set_inactive(self):
        self.is_active = False
        self.save()

    def for_what(self):
        what_list = []
        if self.for_coffee:
            what_list.append('Coffee')

        if self.for_lunch:
            what_list.append('Lunch')

        if self.video_chat:
            what_list.append('Video Chat')

        return ' or '.join(what_list)

    @staticmethod
    def _pretty_print_list(string_list):
        if len(string_list) == 0:
            return ""
        elif len(string_list) == 1:
            return string_list[0]
        else:
            first = string_list[0]
            most = string_list[1:-1]
            last = string_list[-1]
            # 3 or more should have a comma before the 'or'
            # 2 should not have comma before the or
            if most:
                return ', '.join([first] + most) + ', or ' + last
            else:
                return first + ' or ' + last

    def where_text(self):
        return self._pretty_print_list(
            [unicode(loc) for loc in self.locations.all()])

    def departments_text(self):
        selected_depts = self.departments.all()
        if selected_depts.count() == OrgGroup.objects.filter(parent__isnull=True).count():
            return "any department"
        else:
            return self._pretty_print_list(
                [loc.title for loc in selected_depts])

    def find_matching_interests(self):
        """
        Given an interest obj, it will try to match
        against other interest objects that are relevant
        """

        # so far we have the active interests
        interests = Interest.objects.filter(is_active=True, match=None)

        # you cannot match against yourself
        interests = interests.exclude(owner=self.owner)

        meet_type_q = Q(id=None)  # always false -> non-factor in the OR query
        if self.for_lunch:
            meet_type_q = meet_type_q | Q(for_lunch=True)
        if self.for_coffee:
            meet_type_q = meet_type_q | Q(for_coffee=True)
        if self.video_chat:
            meet_type_q = meet_type_q | Q(video_chat=True)
        interests = interests.filter(meet_type_q)

        if not self.video_chat:
            # always false -> non-factor in the OR query
            location_type_q = Q(id=None)
            for location in self.locations.all():
                location_type_q = location_type_q | Q(locations__in=[location])
            interests = interests.filter(location_type_q)

        dept_type_q = Q(id=None)  # always false -> non-factor in the OR query
        for dept in self.departments.all():
            dept_type_q = dept_type_q | Q(departments__in=[dept])
        interests = interests.filter(dept_type_q)

        # order by oldest first
        interests = interests.order_by('created')

        return interests
