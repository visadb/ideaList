from ideaList.models import Item, ItemFrequency, List, Subscription
from django.contrib.auth.models import User
from django import test


class ListTest(test.TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        self.u = User.objects.all()[0]
        self.l1 = List.objects.create(name='List1', owner=self.u)
    def test_fields(self):
        self.assertTrue(List.objects.count() >= 1)
        l = List.objects.all()[0]
        self.assertEqual(l.name, 'List1')
        self.assertEqual(l.owner, self.u)
        self.assertEqual(l.subscribers.count(), 0)
    def test_nontrashed_items(self):
        self.assertEqual(self.l1.nontrashed_items().count(), 0)
        i = Item.objects.create(list=self.l1, text="testitem")
        self.assertEqual(self.l1.nontrashed_items().count(), 1)
        self.assertEqual(self.l1.nontrashed_items()[0].text, 'testitem')
        i.delete()
        self.assertEqual(self.l1.nontrashed_items().count(), 0)
    def test_subscription_for(self):
        self.assertEqual(self.l1.subscription_for(self.u), None)
        s = Subscription.objects.create(user=self.u, list=self.l1)
        self.assertEqual(self.l1.subscription_for(self.u), s)
        u2 = User.objects.all()[1]
        self.assertEqual(self.l1.subscription_for(u2), None)

class ItemTest(test.TestCase):
    def setUp(self):
        self.u = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.l1 = List.objects.create(name='List1', owner=self.u)
        self.i1 = Item.objects.create(list=self.l1, text='testitem')
    def test_fields(self):
        self.assertTrue(Item.objects.count() >= 1)
        i = Item.objects.all()[0]
        self.assertEqual(i.list, self.l1)
        self.assertEqual(i.text, 'testitem')
        self.assertEqual(i.url, '')
        self.assertEqual(i.important, False)
        self.assertEqual(i.position, 0)
    def test_is_on_subscribed_list(self):
        self.assertFalse(self.i1.is_on_subscribed_list(self.u))
        Subscription.objects.create(list=self.l1, user=self.u)
        self.assertTrue(self.i1.is_on_subscribed_list(self.u))


class ItemFrequencyTest(test.TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.s1 = Subscription.objects.create(user=self.u1, list=self.l1)
        self.assertEqual(ItemFrequency.objects.count(), 0)
    def test_increment_new_text(self):
        ItemFrequency.objects.increment(self.l1, 'milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        i = ItemFrequency.objects.all()[0]
        self.assertEqual(i.text, 'milk')
        self.assertEqual(i.frequency, 1)
    def test_increment_old_text(self):
        ItemFrequency.objects.increment(self.l1, 'milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        ItemFrequency.objects.increment(self.l1, 'milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        i = ItemFrequency.objects.all()[0]
        self.assertEqual(i.text, 'milk')
        self.assertEqual(i.frequency, 2)
    def test_increment_two_different(self):
        ItemFrequency.objects.increment(self.l1, 'milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        ItemFrequency.objects.increment(self.l1, 'bread')
        self.assertEqual(ItemFrequency.objects.count(), 2)
        self.assertEqual(ItemFrequency.objects.get(text='milk').frequency, 1)
        self.assertEqual(ItemFrequency.objects.get(text='bread').frequency, 1)
    def test_increment_canonization(self):
        ItemFrequency.objects.increment(self.l1, ' miLk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        ItemFrequency.objects.increment(self.l1, '   milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        self.assertEqual(ItemFrequency.objects.get(text='milk').frequency, 2)
    def test_autoincrement(self):
        Item.objects.create(text='milk', list=self.l1)
        self.assertEqual(ItemFrequency.objects.count(), 1)
        self.assertEqual(ItemFrequency.objects.get(text='milk').frequency, 1)
        Item.objects.create(text='milk', list=self.l1)
        self.assertEqual(ItemFrequency.objects.count(), 1)
        self.assertEqual(ItemFrequency.objects.get(text='milk').frequency, 2)
        Item.objects.create(text='bread', list=self.l1)
        self.assertEqual(ItemFrequency.objects.count(), 2)
        self.assertEqual(ItemFrequency.objects.get(text='milk').frequency, 2)
        self.assertEqual(ItemFrequency.objects.get(text='bread').frequency, 1)
    def test_frequents_by_list_with_no_limit(self):
        for t in ('a','b','c','b','c','c'):
            Item.objects.create(text=t, list=self.l1)
        f = ItemFrequency.objects.frequents_by_list(self.u1)
        self.assertIn(self.l1.id, f)
        self.assertEqual(len(f[self.l1.id]), 3)
        self.assertEqual(f[self.l1.id], ['c','b','a'])
    def test_frequents_by_list_with_limit(self):
        for t in ('a','b','c','b','c','c'):
            Item.objects.create(text=t, list=self.l1)
        f = ItemFrequency.objects.frequents_by_list(self.u1, limit=2)
        self.assertIn(self.l1.id, f)
        self.assertEqual(len(f[self.l1.id]), 2)
        self.assertEqual(f[self.l1.id], ['c','b'])


class SubscriptionTest(test.TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.s = Subscription.objects.create(user=self.u1,list=self.l1)
    def test_fields(self):
        self.assertTrue(Subscription.objects.count() >= 1)
        s = Subscription.objects.all()[0]
        self.assertEqual(s.user, self.u1)
        self.assertEqual(s.list, self.l1)
        self.assertEqual(s.position, 0)

# Test the nontrash_subscriptions manager injected into User
class UserNontrashSubscriptionsTest(test.TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('pena', 'lol@lol.lol', 'passwd')
        self.u2 = User.objects.create_user('tena', 'lol2@lol.lol', 'passwd')
        self.subd_list = List.objects.create(name='List1', owner=self.u1)
        self.subd_list_sub_trashed = List.objects.create(name='List2',
                owner=self.u1)
        self.trashed_subd_list = List.objects.create(name='List3',owner=self.u1)
        self.unsubd_list = List.objects.create(name='List4', owner=self.u1)
        self.s1 = Subscription.objects.create(user=self.u1,list=self.subd_list)
        self.s2 = Subscription.objects.create(user=self.u1,
                list=self.subd_list_sub_trashed)
        self.s2.delete()
        self.s3 = Subscription.objects.create(user=self.u1,
                list=self.trashed_subd_list)
        self.trashed_subd_list.delete()
        self.s4 = Subscription.objects.create(user=self.u2,
                list=self.unsubd_list)

    def test_only_subd_list_contained(self):
        self.assertEqual(self.u1.nontrash_subscriptions.count(), 1)
        cnt = self.u1.nontrash_subscriptions.filter(list__name='List1').count()
        self.assertEqual(cnt, 1)

    def test_subd_list_sub_trashed_not_contained(self):
        cnt = self.u1.nontrash_subscriptions.filter(list__name='List2').count()
        self.assertEqual(cnt, 0)

    def test_trashed_subd_list_not_contained(self):
        cnt = self.u1.nontrash_subscriptions.filter(list__name='List3').count()
        self.assertEqual(cnt, 0)

    def test_unsubd_list_not_contained(self):
        cnt = self.u1.nontrash_subscriptions.filter(list__name='List4').count()
        self.assertEqual(cnt, 0)
