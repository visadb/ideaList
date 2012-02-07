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
        self.assertEqual(ItemFrequency.objects.count(), 0)
    def test_increment_new_text(self):
        ItemFrequency.objects.increment('milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        i = ItemFrequency.objects.all()[0]
        self.assertEqual(i.text, 'milk')
        self.assertEqual(i.frequency, 1)
    def test_increment_old_text(self):
        ItemFrequency.objects.increment('milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        ItemFrequency.objects.increment('milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        i = ItemFrequency.objects.all()[0]
        self.assertEqual(i.text, 'milk')
        self.assertEqual(i.frequency, 2)
    def test_increment_two_different(self):
        ItemFrequency.objects.increment('milk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        ItemFrequency.objects.increment('bread')
        self.assertEqual(ItemFrequency.objects.count(), 2)
        self.assertEqual(ItemFrequency.objects.get(text='milk').frequency, 1)
        self.assertEqual(ItemFrequency.objects.get(text='bread').frequency, 1)
    def test_increment_canonization(self):
        ItemFrequency.objects.increment(' miLk')
        self.assertEqual(ItemFrequency.objects.count(), 1)
        ItemFrequency.objects.increment('   milk')
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
    def test_frequent_list_with_no_limit(self):
        for t in ('a','b','c','b','c','c'):
            Item.objects.create(text=t, list=self.l1)
        f = ItemFrequency.objects.frequent_list()
        self.assertEqual(len(f), 3)
        self.assertEqual(f, ['c','b','a'])
    def test_frequent_list_with_limit(self):
        for t in ('a','b','c','b','c','c'):
            Item.objects.create(text=t, list=self.l1)
        f = ItemFrequency.objects.frequent_list(limit=2)
        self.assertEqual(len(f), 2)
        self.assertEqual(f, ['c','b'])



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
