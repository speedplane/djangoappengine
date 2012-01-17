from __future__ import with_statement
import warnings

from django.db import models
from django.db.utils import DatabaseError
from django.test import TestCase


# TODO: Move to djangotoolbox or django.db.utils?
class DatabaseWarning:
     pass


class KeysTest(TestCase):
    """
    GAE requires that keys are strings or positive integers,
    keys also play a role in defining entity groups.

    See: http://code.google.com/appengine/docs/python/datastore/keyclass.html.
    """

    def setUp(self):
        self.save_warnings_state()

    def tearDown(self):
        self.restore_warnings_state()

    def test_native(self):
        """
        Strings and positive integers can be directly represented when
        used as keys.

        TODO: GAE should use GAEKeyField on default that should work at
              least with both strings and ints (by using the underlying db.Key type)?
        TODO: Add GAEKeyField specific tests here.
        """

        class NativeKey(models.Model):
           pass
        NativeKey.objects.create(pk=1)
#        NativeKey.objects.create(pk='a') TODO: ?

    def test_nonnative(self):
        """
        TODO: Trying to use a nonnative primary key should work as long
        as the field type can be represented by the back-end type, but
        it should also warn the user about lossy conversions, unexpected
        sorting, value limitation or potential future ramifications.

        TODO: It may be even better to raise exceptions / issue 
        warnings during model validation.
        """

        warnings.simplefilter('error', DatabaseWarning)

        # This one can be exactly represented.
        class CharKey(models.Model):
            id = models.CharField(primary_key=True, max_length=10)
        CharKey.objects.create(id='a')

#        # Warning with a range limitation.
#        with self.assertRaises(DatabaseWarning):
#            class IntegerKey(models.Model):
#                id = models.IntegerField(primary_key=True)
#            IntegerKey.objects.create(id=1)

#        # Some rely on unstable assumptions and should warn.
#        with self.assertRaises(DatabaseWarning):
#            class DateKey(models.Model):
#                id = models.DateField(primary_key=True, auto_now=True)
#            DateKey.objects.create()

#        with self.assertRaises(DatabaseWarning):
#            class EmailKey(models.Model):
#               id = models.EmailField(primary_key=True)
#            EmailKey.objects.create(id='aaa@example.com')

        # Some cannot be reasonably represented (e.g. binary or string
        # encoding would prevent comparisons to work as expected).
        with self.assertRaises(DatabaseError):
            class FloatKey(models.Model):
                id = models.FloatField(primary_key=True)
            FloatKey.objects.create(id=1.0)

#        with self.assertRaises(DatabaseError):
#           class DecimalKey(models.Model):
#              id = models.DecimalField(primary_key=True, decimal_places=2, max_digits=5)
#           DecimalKey.objects.create(id=1)

    def test_casting(self):
        """
        Creation and lookups should use the same type casting as
        vanilla Django does.

        Casting for GAEKeyField should encompass both CharField and
        IntegerField rules.
        """

        class NativeKey(models.Model):
            pass
        NativeKey.objects.create(id=1)
        NativeKey.objects.create(id=1.1)
#        NativeKey.objects.create(id='a') # TODO: GAEKeyField again?
        NativeKey.objects.filter(id__gt=1)
        NativeKey.objects.filter(id__gt=1.1)
        NativeKey.objects.filter(id__gt='a')

        class CharKey(models.Model):
            id = models.CharField(primary_key=True, max_length=10)
        CharKey.objects.create(id=1)
        CharKey.objects.create(id=1.1)
        CharKey.objects.create(id='a')
        CharKey.objects.filter(id__gt=1)
        CharKey.objects.filter(id__gt=1.1)
        CharKey.objects.filter(id__gt='a')

        class IntegerKey(models.Model):
            id = models.IntegerField(primary_key=True)
        IntegerKey.objects.create(id=1)
        IntegerKey.objects.create(id=1.1)
        with self.assertRaises(ValueError):
            IntegerKey.objects.create(id='a')
        IntegerKey.objects.filter(id__gt='1')
        IntegerKey.objects.filter(id__gt=1.1)
        with self.assertRaises(ValueError):
            IntegerKey.objects.filter(id__gt='a')

    def test_nonpositive_integers(self):
        """
        Nonpositive keys are not allowed on GAE, and trying to use them
        to create or look up objects should raise a database exception.
        """

        class NativeKey(models.Model):
            pass
        with self.assertRaises(DatabaseError):
            NativeKey.objects.create(id=-1)
        with self.assertRaises(DatabaseError):
            NativeKey.objects.create(id=0)
        with self.assertRaises(DatabaseError):
            NativeKey.objects.get(id=-1)
        with self.assertRaises(DatabaseError):
            NativeKey.objects.get(id__gt=-1)
#        with self.assertRaises(DatabaseError):
#            NativeKey.objects.filter(id__gt=-1) # TODO: ?
#        with self.assertRaises(DatabaseError):
#            NativeKey.objects.get(id=0) # TODO: ?
        with self.assertRaises(DatabaseError):
            NativeKey.objects.get(id__gt=0)
#        with self.assertRaises(DatabaseError):
#            NativeKey.objects.filter(id__gt=0) # TODO: ?

        class IntegerKey(models.Model):
            id = models.IntegerField(primary_key=True)
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.create(id=-1)
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.create(id=0)
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.get(id=-1) # TODO: Sometimes gives a DatabaseException and sometimes a DoesNotExist?
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.get(id__gt=-1)
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.filter(id__gt=-1) # TODO: ?
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.get(id=0) # TODO: DatabaseException rather than DoesNotExist,
        with self.assertRaises(DatabaseError):
            IntegerKey.objects.get(id__gt=0)
#        with self.assertRaises(DatabaseError):
#            IntegerKey.objects.filter(id__gt=0) # TODO: ?
