from __future__ import with_statement

from django.db import models
from django.db.utils import DatabaseError
from django.test import TestCase


class KeysTest(TestCase):
    """
    GAE requires that keys are strings or positive integers.
    Test that each usage of a bad key results in an exception.

    See: http://code.google.com/appengine/docs/python/datastore/keyclass.html#Key_from_path.
    """

    def test_native(self):
        """
        Strings and positive integers are allowed as keys.
        Note: creating a QuerySets is not enough for this test, you
        have to make them execute (e.g. by casting to a list).
        """

        class JustKey(models.Model):
           pass
#        self.assertEqual(list(JustKey.objects.filter(pk='a')), []) # TODO: ?
        self.assertEqual(list(JustKey.objects.filter(pk=1)), [])

        class IntegerKey(models.Model):
            id = models.IntegerField(primary_key=True)
        o = IntegerKey.objects.create(id=1)
        self.assertEqual(list(IntegerKey.objects.filter(id=1)), [o])
#        self.assertEqual(list(IntegerKey.objects.filter(id='a')), []) # TODO: ?

        class CharKey(models.Model):
            id = models.CharField(primary_key=True, max_length=10)
        o = CharKey.objects.create(id='a')
        self.assertEqual(list(CharKey.objects.filter(id='a')), [o])
#        self.assertEqual(list(CharKey.objects.filter(id=1)), [o]) # TODO: ?

    def test_bad_types(self):
        """Only strings, ints and longs should be used as keys."""

        with self.assertRaises(DatabaseError):
            class DateKey(models.Model):
                id = models.DateField(primary_key=True, auto_now=True)
            DateKey.objects.create()

        with self.assertRaises(DatabaseError):
            class FloatKey(models.Model):
                id = models.FloatField(primary_key=True)
            FloatKey.objects.create(id=1.0)

        # TODO: The following work, should they?
#        with self.assertRaises(DatabaseError):
#           class BooleanKey(models.Model):
#              id = models.BooleanField(primary_key=True)
#           BooleanKey.objects.create(id=True)

#        with self.assertRaises(DatabaseError):
#           class DecimalKey(models.Model):
#              id = models.DecimalField(primary_key=True)
#           DecimalKey.objects.create(id=1)

    def test_bad_type_lookups(self):
        """
        Trying to use a nonallowed type as a filter value for a key,
        should raise an exception.
        """

        class IntegerKey(models.Model):
            id = models.IntegerField(primary_key=True)
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.filter(id__gt=1.1) # TODO: ?
#        with self.assertRaises(DatabaseError):
#           IntegerKey.objects.filter(id__gt='1') # TODO: ?

        class CharKey(models.Model):
            id = models.CharField(primary_key=True, max_length=10)
#        with self.assertRaises(DatabaseError):
#            CharKey.objects.filter(id__gt=1.1) # TODO: ?
#        with self.assertRaises(DatabaseError):
#            CharKey.objects.filter(id__gt=1) # TODO: ?

    def test_nonpositive_integers(self):
        """
        Nonpositive keys are not allowed on GAE, and trying to use them
        to create objects should raise an exception.
        """

        class NonpositiveIntegerKey(models.Model):
            id = models.IntegerField(primary_key=True)
        with self.assertRaises(DatabaseError):
            NonpositiveIntegerKey.objects.create(id=-1)
        with self.assertRaises(DatabaseError):
            NonpositiveIntegerKey.objects.create(id=0)

    def test_nonpositive_integer_lookups(self):
        """
        Filtering can't be made to work consistently with nonpositive
        integers, so better if it raises exceptions in each case.
        """

        class IntegerKey(models.Model):
            id = models.IntegerField(primary_key=True)
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.get(id=-1) # TODO: Also DatabaseException, not a DoesNotExist?
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.get(id__gt=-1)
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.filter(id__gt=-1) # TODO: ?
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.get(id=0) # TODO: ?
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.get(id__gt=0)
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.filter(id__gt=0) # TODO: ?
