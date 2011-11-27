from django.conf import settings
from django.db.models import loading
from django.core.management import call_command
from django.contrib.auth.models import User
import django.test
from undelete.testmodels.models import Apple

class TestCase(django.test.TestCase):
    """
    Custom TestCase class that supports models that exist only in tests.
    """
    apps = ('undelete.testmodels',)
    def _pre_setup(self):
        # Add the models to the db.
        self._original_installed_apps = list(settings.INSTALLED_APPS)
        for app in self.apps:
            settings.INSTALLED_APPS.append(app)
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, migrate=False, verbosity=0)
        # Call the original method that does the fixtures etc.
        super(TestCase, self)._pre_setup()

    def _post_teardown(self):
        # Call the original method.
        super(TestCase, self)._post_teardown()
        # Restore the settings.
        settings.INSTALLED_APPS = self._original_installed_apps
        loading.cache.loaded = False

class TrashableTest(TestCase):
    def test_trashed_at(self):
        a1 = Apple.objects.create(color="red")
        self.assertEqual(a1.color, "red")
        self.assertIsNone(a1.trashed_at)
        a1.delete()
        self.assertIsNotNone(a1.trashed_at)

    def test_is_trash(self):
        a1 = Apple.objects.create(color="red")
        a2 = Apple.objects.create(color="green")
        self.assertFalse(a1.is_trash())
        self.assertFalse(a2.is_trash())
        a1.delete()
        self.assertTrue(a1.is_trash())
        self.assertFalse(a2.is_trash())
        a1.restore()
        self.assertFalse(a1.is_trash())
        self.assertFalse(a2.is_trash())

    def test_manager_counts(self):
        self.assertEqual(Apple.objects.count(), 0)
        self.assertEqual(Apple.nontrash.count(), 0)
        self.assertEqual(Apple.trash.count(), 0)
        a1 = Apple.objects.create(color="red")
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.nontrash.count(), 1)
        self.assertEqual(Apple.trash.count(), 0)
        a1.delete()
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.nontrash.count(), 0)
        self.assertEqual(Apple.trash.count(), 1)
        a1.restore()
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.nontrash.count(), 1)
        self.assertEqual(Apple.trash.count(), 0)
        a1.delete(trash=False)
        self.assertEqual(Apple.objects.count(), 0)
        self.assertEqual(Apple.nontrash.count(), 0)
        self.assertEqual(Apple.trash.count(), 0)

    def test_double_delete(self):
        self.assertEqual(Apple.objects.count(), 0)
        a1 = Apple.objects.create(color="red")
        self.assertEqual(Apple.objects.count(), 1)
        a1.delete()
        self.assertEqual(Apple.objects.count(), 1)
        a1.delete()
        self.assertEqual(Apple.objects.count(), 0)

    def test_empty_trash(self):
        Apple.empty_trash()
        self.assertEqual(Apple.objects.count(), 0)
        self.assertEqual(Apple.trash.count(), 0)
        a1 = Apple.objects.create(color="red")
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.trash.count(), 0)
        a1.empty_trash()
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.trash.count(), 0)
        a1.delete()
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.trash.count(), 1)
        a1.empty_trash()
        self.assertEqual(Apple.objects.count(), 0)
        self.assertEqual(Apple.trash.count(), 0)

    def test_empty_trash2(self):
        a1 = Apple.objects.create(color="red")
        Apple.objects.create(color="green")
        self.assertEqual(Apple.objects.count(), 2)
        self.assertEqual(Apple.trash.count(), 0)
        Apple.empty_trash()
        self.assertEqual(Apple.objects.count(), 2)
        self.assertEqual(Apple.trash.count(), 0)
        a1.delete()
        self.assertEqual(Apple.objects.count(), 2)
        self.assertEqual(Apple.trash.count(), 1)
        Apple.empty_trash()
        self.assertEqual(Apple.objects.count(), 1)
        self.assertEqual(Apple.trash.count(), 0)
        self.assertEqual(Apple.objects.all()[0].color, "green")

class TrashablePositionTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('user1', 'lol@lol.lol', 'password')
        self.u2 = User.objects.create_user('user2', 'lol@lol.lol', 'password')
