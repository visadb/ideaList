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
        self.assertEqual(i.priority, u'NO')
        self.assertEqual(i.position, 0)

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
        self.assertEqual(s.minimized, False)
        self.assertEqual(s.position, 0)

#class LogTest(test.TestCase):
#    fixtures = ['auth.json']
#    def setUp(self):
#        self.setup_time = datetime.now()
#    def test_newer_than(self):
#        self.assertEqual(LogEntry.objects.newer_than(self.setup_time).count(),0)
#        self.l = List.objects.create(name='List1', owner=User.objects.all()[0])
#        d2 = datetime.now()
#        self.assertEqual(LogEntry.objects.newer_than(self.setup_time).count(),1)
#        self.assertEqual(LogEntry.objects.newer_than(d2).count(),0)
#
#class LogDetectTest(test.TestCase):
#    fixtures = ['auth.json']
#    def setUp(self):
#        self.setup_time = datetime.now()
#        self.u1, self.u2 = User.objects.all()[:2]
#        self.assertEqual(LogEntry.objects.count(), 0)
#        self.l = List.objects.create(name='List1', owner=self.u1)
#        self.assertEqual(LogEntry.objects.count(), 1)
#    def test_list_add(self):
#        le = LogEntry.objects.all()[0]
#        self.assertIs(List, le.content_type.model_class())
#        self.assertEqual(self.l, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.ADD)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_list_update(self):
#        self.l.name = 'List2'
#        self.l.save()
#        self.assertEqual(LogEntry.objects.count(), 2)
#        updates = LogEntry.objects.filter(change_type=LogEntry.UPDATE)
#        self.assertEqual(updates.count(), 1)
#        le = updates[0]
#        self.assertIs(List, le.content_type.model_class())
#        self.assertEqual(self.l, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.UPDATE)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_list_delete(self):
#        self.l.delete()
#        self.assertEqual(LogEntry.objects.count(), 2)
#        deletes = LogEntry.objects.filter(change_type=LogEntry.DELETE)
#        self.assertEqual(deletes.count(), 1)
#        le = deletes[0]
#        self.assertIs(List, le.content_type.model_class())
#        self.assertEqual(self.l, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.DELETE)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_list_undelete(self):
#        self.l.delete()
#        self.assertEqual(LogEntry.objects.count(), 2)
#        self.l.restore()
#        self.assertEqual(LogEntry.objects.count(), 3)
#        undeletes = LogEntry.objects.filter(change_type=LogEntry.UNDELETE)
#        self.assertEqual(undeletes.count(), 1)
#        le = undeletes[0]
#        self.assertIs(List, le.content_type.model_class())
#        self.assertEqual(self.l, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.UNDELETE)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_subscription_add(self):
#        s = Subscription.objects.create(user=self.u1, list=self.l)
#        le = LogEntry.objects.latest()
#        self.assertIs(Subscription, le.content_type.model_class())
#        self.assertEqual(s, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.ADD)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_subscription_update(self):
#        s = Subscription.objects.create(user=self.u1, list=self.l)
#        s.minimized = True
#        s.save()
#        le = LogEntry.objects.latest()
#        self.assertIs(Subscription, le.content_type.model_class())
#        self.assertEqual(s, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.UPDATE)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_subscription_delete(self):
#        s = Subscription.objects.create(user=self.u1, list=self.l)
#        s.delete()
#        le = LogEntry.objects.latest()
#        self.assertIs(Subscription, le.content_type.model_class())
#        self.assertEqual(s, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.DELETE)
#        self.assertTrue(le.time >= self.setup_time)
#    def test_subscription_undelete(self):
#        s = Subscription.objects.create(user=self.u1, list=self.l)
#        s.delete()
#        s.restore()
#        le = LogEntry.objects.latest()
#        self.assertIs(Subscription, le.content_type.model_class())
#        self.assertEqual(s, le.content_object)
#        self.assertEqual(le.change_type, LogEntry.UNDELETE)
#        self.assertTrue(le.time >= self.setup_time)
#
#class LogInstructionTest(test.TestCase):
#    fixtures = ['auth.json']
#    def setUp(self):
#        self.u1, self.u2 = User.objects.all()[:2]
#        self.l1 = List.objects.create(name='List1', owner=self.u1)
#        self.assertIsNone(LogEntry.objects.latest().client_instruction(self.u1),
#                'List add should not cause any client action')
#        self.l2 = List.objects.create(name='List2', owner=self.u1)
#        self.s = Subscription.objects.create(user=self.u1,list=self.l1)
#    def assertKeys(self, ci):
#        self.assertIsNotNone(ci)
#        self.assertTrue('action' in ci)
#        self.assertTrue('content_type' in ci)
#        self.assertTrue('object' in ci)
#    def test_add_subscription(self):
#        # Subscription added as last part of setUp
#        le = LogEntry.objects.latest()
#        self.assertEqual(le.content_object, self.s)
#        ci_u1 = le.client_instruction(self.u1)
#        self.assertKeys(ci_u1)
#        self.assertEqual(ci_u1['action'], 'add')
#        self.assertEqual(ci_u1['content_type'], 'subscription')
#        ci_u2 = le.client_instruction(self.u2)
#        self.assertIsNone(ci_u2,
#                'Adding a subscription yielded an instruction for unrelated user')
#    def test_add_item(self):
#        i = Item.objects.create(list=self.l1, text='testitem')
#        le = LogEntry.objects.latest()
#        self.assertEqual(le.content_object, i)
#        ci_u1 = le.client_instruction(self.u1)
#        self.assertKeys(ci_u1)
#        self.assertEqual(ci_u1['action'], 'update')
#        self.assertEqual(ci_u1['content_type'], 'subscription')
#        ci_u2 = le.client_instruction(self.u2)
#        self.assertIsNone(ci_u2,
#                'Adding a item yielded an instruction for unrelated user')
#    def test_update_item(self):
#        i = Item.objects.create(list=self.l1, text='testitem')
#        i.text="updated testitem"
#        i.save()
#        le = LogEntry.objects.latest()
#        self.assertEqual(le.content_object, i)
#        ci_u1 = le.client_instruction(self.u1)
#        self.assertKeys(ci_u1)
#        self.assertEqual(ci_u1['action'], 'update')
#        self.assertEqual(ci_u1['content_type'], 'subscription')
#    def test_list_delete(self):
#        self.l1.delete()
#        le = LogEntry.objects.latest()
#        self.assertEqual(le.content_object, self.l1)
#        ci_u1 = le.client_instruction(self.u1)
#        self.assertKeys(ci_u1)
#        self.assertEqual(ci_u1['action'], 'remove')
#        self.assertEqual(ci_u1['content_type'], 'subscription')
#        ci_u2 = le.client_instruction(self.u2)
#        self.assertIsNone(ci_u2,
#                'Deleting a list yielded an instruction for unrelated user')
#    def test_list_undelete(self):
#        self.l1.delete()
#        self.l1.restore()
#        le = LogEntry.objects.latest()
#        self.assertEqual(le.content_object, self.l1)
#        ci_u1 = le.client_instruction(self.u1)
#        self.assertKeys(ci_u1)
#        self.assertEqual(ci_u1['action'], 'add')
#        self.assertEqual(ci_u1['content_type'], 'subscription')
