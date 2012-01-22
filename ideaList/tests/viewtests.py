import json
from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ideaList.models import List, Item, Subscription

class MyViewTest(test.TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        self.c = Client()
        self.u1 = User.objects.get(username='visa')
        self.u2 = User.objects.get(username='nanda')
        self.assertTrue(self.c.login(username='visa', password='salakala'))
    def check_login_required(self, viewname):
        self.c.logout()
        r = self.c.get(reverse(viewname))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.has_header('Location'))
        self.assertIn(reverse('django.contrib.auth.views.login'),
                r.get('Location', None))
    # Returns the parsed JSON response data
    def check_state_in_response(self, r):
        try:
            response_data = json.loads(r.content)
        except ValueError:
            self.fail('Response was not valid JSON')
        self.assertIn('state', response_data)
        return response_data

class MainViewTest(MyViewTest):
    def test_login_required(self):
        self.check_login_required('ideaList.views.main')
    def test_get(self):
        r = self.c.get(reverse('ideaList.views.main'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('init_state', r.context)
        self.assertIn('ideaList/main.html', [t.name for t in r.templates])

class GetStateViewTest(MyViewTest):
    def test_login_required(self):
        self.check_login_required('ideaList.views.get_state')
    def test_get(self):
        r = self.c.get(reverse('ideaList.views.get_state'))
        self.assertEqual(r.status_code, 200)
        self.check_state_in_response(r)

class AddSubscriptionViewTest(MyViewTest):
    def setUp(self):
        super(AddSubscriptionViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=self.u1)
    def test_login_required(self):
        self.check_login_required('ideaList.views.add_subscription')
    def test_subscribe_to_nonexistent_list(self):
        self.assertEqual(Subscription.objects.count(), 0)
        r = self.c.post(reverse('ideaList.views.add_subscription'),
                {'list_id':self.l1.id+1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.check_state_in_response(r)
    def test_add_new_subscription(self):
        self.assertEqual(Subscription.objects.count(), 0)
        r = self.c.post(reverse('ideaList.views.add_subscription'),
                {'list_id':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        data = self.check_state_in_response(r)
        self.assertIn('msg', data)
        self.assertIn('created', data['msg'])
        self.assertEqual(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEqual(s.list, self.l1)
        self.assertEqual(s.user, self.u1)
    def test_add_duplicate_subscription(self):
        self.assertEqual(Subscription.objects.count(), 0)
        s = Subscription.objects.create(list=self.l1, user=self.u1)
        self.assertEqual(Subscription.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.add_subscription'),
                {'list_id':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        data = self.check_state_in_response(r)
        self.assertIn('msg', data)
        self.assertIn('Already subscribed', data['msg'])
        self.assertEqual(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEqual(s.list, self.l1)
        self.assertEqual(s.user, self.u1)
    def test_add_restore_subscription(self):
        self.assertEqual(Subscription.objects.count(), 0)
        s = Subscription.objects.create(list=self.l1, user=self.u1,
                minimized=False)
        self.assertEqual(Subscription.objects.count(), 1)
        s.minimized = True
        s.save()
        s.delete()
        self.assertEqual(Subscription.trash.count(), 1)
        r = self.c.post(reverse('ideaList.views.add_subscription'),
                {'list_id':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        data = self.check_state_in_response(r)
        self.assertIn('msg', data)
        self.assertIn('restored', data['msg'])
        self.assertEqual(Subscription.trash.count(), 0)
        self.assertEqual(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEqual(s.list, self.l1)
        self.assertEqual(s.user, self.u1)
        self.assertTrue(s.minimized)

class RemoveSubscriptionViewTest(MyViewTest):
    def setUp(self):
        super(RemoveSubscriptionViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.s1 = Subscription.objects.create(list=self.l1, user=self.u1)
    def test_login_required(self):
        self.check_login_required('ideaList.views.remove_subscription')
    def test_remove_subscription(self):
        self.assertEqual(Subscription.trash.count(), 0)
        self.assertEqual(Subscription.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.remove_subscription'),
                {'list_id':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.check_state_in_response(r)
        self.assertEqual(Subscription.trash.count(), 1)
        self.assertEqual(Subscription.objects.count(), 1)
    def test_remove_subscription_from_nonexistent_list(self):
        self.assertEqual(Subscription.trash.count(), 0)
        self.assertEqual(Subscription.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.remove_subscription'),
                {'list_id':self.l1.id+1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.check_state_in_response(r)
        self.assertEqual(Subscription.trash.count(), 0)
        self.assertEqual(Subscription.objects.count(), 1)
    def test_remove_nonexistent_subscription(self):
        self.s1.delete()
        self.assertEqual(Subscription.trash.count(), 1)
        self.assertEqual(Subscription.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.remove_subscription'),
                {'list_id':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.check_state_in_response(r)
        self.assertEqual(Subscription.trash.count(), 1)
        self.assertEqual(Subscription.objects.count(), 1)

class MoveSubscriptionViewTest(MyViewTest):
    def setUp(self):
        super(MoveSubscriptionViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.l2 = List.objects.create(name='List2', owner=self.u1)
        self.l3 = List.objects.create(name='List3', owner=self.u1)
        self.s1 = Subscription.objects.create(list=self.l1, user=self.u1)
        self.s2 = Subscription.objects.create(list=self.l2, user=self.u1)
        self.s3 = Subscription.objects.create(list=self.l3, user=self.u1)
        self.assertEqual(self.s1.position, 0)
        self.assertEqual(self.s2.position, 1)
        self.assertEqual(self.s3.position, 2)
    def test_login_required(self):
        self.check_login_required('ideaList.views.move_subscription')
    def test_move_up(self):
        r = self.c.post(reverse('ideaList.views.move_subscription'),
                {'subscription_id':self.s2.id, 'where':'up'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Subscription.objects.get(pk=self.s2.id).position, 0)
        self.assertEqual(Subscription.objects.get(pk=self.s1.id).position, 1)
        self.check_state_in_response(r)
    def test_move_upmost_up(self):
        r = self.c.post(reverse('ideaList.views.move_subscription'),
                {'subscription_id':self.s1.id, 'where':'up'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Subscription.objects.get(pk=self.s1.id).position, 0)
        self.assertEqual(Subscription.objects.get(pk=self.s2.id).position, 1)
        self.check_state_in_response(r)
    def test_move_down(self):
        r = self.c.post(reverse('ideaList.views.move_subscription'),
                {'subscription_id':self.s2.id, 'where':'down'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Subscription.objects.get(pk=self.s2.id).position, 2)
        self.assertEqual(Subscription.objects.get(pk=self.s3.id).position, 1)
        self.check_state_in_response(r)
    def test_move_down_across_trashed_subscription(self):
        self.s2.delete()
        r = self.c.post(reverse('ideaList.views.move_subscription'),
                {'subscription_id':self.s1.id, 'where':'down'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Subscription.objects.get(pk=self.s1.id).position, 2)
        self.assertEqual(Subscription.objects.get(pk=self.s2.id).position, 0)
        self.assertEqual(Subscription.objects.get(pk=self.s3.id).position, 1)
        self.check_state_in_response(r)
    def test_move_up_across_trashed_subscription(self):
        self.s2.delete()
        r = self.c.post(reverse('ideaList.views.move_subscription'),
                {'subscription_id':self.s3.id, 'where':'up'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Subscription.objects.get(pk=self.s1.id).position, 1)
        self.assertEqual(Subscription.objects.get(pk=self.s2.id).position, 2)
        self.assertEqual(Subscription.objects.get(pk=self.s3.id).position, 0)
        self.check_state_in_response(r)
    def test_move_abs(self):
        r = self.c.post(reverse('ideaList.views.move_subscription'),
                {'subscription_id':self.s1.id, 'where':2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Subscription.objects.get(pk=self.s1.id).position, 2)
        self.assertEqual(Subscription.objects.get(pk=self.s2.id).position, 0)
        self.assertEqual(Subscription.objects.get(pk=self.s3.id).position, 1)
        self.check_state_in_response(r)

class SubscriptionMinimizationViewsTest(MyViewTest):
    def setUp(self):
        super(SubscriptionMinimizationViewsTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.s1 = Subscription.objects.create(list=self.l1, user=self.u1)
        self.assertFalse(self.s1.minimized)
    def test_login_required(self):
        self.check_login_required('ideaList.views.minimize_subscription')
        self.check_login_required('ideaList.views.maximize_subscription')
    def test_minimize(self):
        r = self.c.post(reverse('ideaList.views.minimize_subscription'),
                {'subscription_id':self.s1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Subscription.objects.get(pk=self.s1.id).minimized)
        self.check_state_in_response(r)
    def test_maximize(self):
        self.s1.minimized = True
        self.s1.save()
        self.assertTrue(Subscription.objects.get(pk=self.s1.id).minimized)
        r = self.c.post(reverse('ideaList.views.maximize_subscription'),
                {'subscription_id':self.s1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Subscription.objects.get(pk=self.s1.id).minimized)
        self.check_state_in_response(r)
    def test_minimize_other_users_subscription(self):
        s2 = Subscription.objects.create(list=self.l1, user=self.u2)
        self.assertFalse(Subscription.objects.get(pk=s2.id).minimized)
        r = self.c.post(reverse('ideaList.views.minimize_subscription'),
                {'subscription_id':s2.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Subscription.objects.get(pk=s2.id).minimized)
        self.check_state_in_response(r)
    def test_minimize_with_missing_sub_id(self):
        r = self.c.post(reverse('ideaList.views.minimize_subscription'),
                {'subscription_id_MISSPELLED':self.s1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Subscription.objects.get(pk=self.s1.id).minimized)
        self.check_state_in_response(r)
    def test_minimize_with_nonexisting_id(self):
        r = self.c.post(reverse('ideaList.views.minimize_subscription'),
                {'subscription_id':self.s1.id+123},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.assertFalse(Subscription.objects.get(pk=self.s1.id).minimized)
        self.check_state_in_response(r)
    def test_minimize_with_invalid_id(self):
        r = self.c.post(reverse('ideaList.views.minimize_subscription'),
                {'subscription_id':'INVALID'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Subscription.objects.get(pk=self.s1.id).minimized)
        self.check_state_in_response(r)

class RemoveItemViewTest(MyViewTest):
    def setUp(self):
        super(RemoveItemViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.s1 = Subscription.objects.create(list=self.l1, user=self.u1)
        self.i1 = Item.objects.create(list=self.l1, text='testitem1')
        self.i2 = Item.objects.create(list=self.l1, text='testitem2')
        self.i3 = Item.objects.create(list=self.l1, text='testitem3')
        self.assertEqual(Item.objects.count(), 3)
        self.assertEqual(Item.nontrash.count(), 3)
    def test_login_required(self):
        self.check_login_required('ideaList.views.remove_items')
    def test_valid_item_id(self):
        r = self.c.post(reverse('ideaList.views.remove_items'),
                {'item_ids':self.i1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.trash.count(), 1)
        self.assertEqual(Item.nontrash.count(), 2)
        self.check_state_in_response(r)
    def test_valid_item_ids(self):
        r = self.c.post(reverse('ideaList.views.remove_items'),
                {'item_ids':(self.i1.id, self.i3.id)},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.trash.count(), 2)
        self.assertEqual(Item.nontrash.count(), 1)
        self.check_state_in_response(r)
    def test_not_own_item(self):
        self.s1.delete()
        r = self.c.post(reverse('ideaList.views.remove_items'),
                {'item_ids':self.i1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Item.trash.count(), 0)
        self.assertEqual(Item.nontrash.count(), 3)
        self.check_state_in_response(r)
    def test_item_ids_missing(self):
        r = self.c.post(reverse('ideaList.views.remove_items'),
                {'item_ids_mispelled':self.i1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.nontrash.count(), 3)
        self.check_state_in_response(r)
    def test_invalid_item_id(self):
        r = self.c.post(reverse('ideaList.views.remove_items'),
                {'item_ids':'invalid'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.nontrash.count(), 3)
        self.check_state_in_response(r)
    def test_nonexisting_item_id(self):
        r = self.c.post(reverse('ideaList.views.remove_items'),
                {'item_ids':self.i1.id+100},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(Item.nontrash.count(), 3)
        self.check_state_in_response(r)

class MoveItemViewTest(MyViewTest):
    def setUp(self):
        super(MoveItemViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=User.objects.all()[0])
        self.l2 = List.objects.create(name='List2', owner=User.objects.all()[0])
        self.i1 = Item.objects.create(list=self.l1, text='testitem1-1')
        self.i2 = Item.objects.create(list=self.l1, text='testitem1-2')
        self.i3 = Item.objects.create(list=self.l1, text='testitem1-3')
        self.i4 = Item.objects.create(list=self.l2, text='testitem2-1')
        self.i5 = Item.objects.create(list=self.l2, text='testitem2-2')
        self.assertEqual(self.i1.position, 0)
        self.assertEqual(self.i2.position, 1)
        self.assertEqual(self.i3.position, 2)
        self.assertEqual(self.i4.position, 0)
        self.assertEqual(self.i5.position, 1)
    def test_login_required(self):
        self.check_login_required('ideaList.views.move_item')
    def test_move_up(self):
        r = self.c.post(reverse('ideaList.views.move_item'),
                {'item_id':self.i2.id, 'where':'up'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i2.id).position, 0)
        self.assertEqual(Item.objects.get(pk=self.i1.id).position, 1)
        self.check_state_in_response(r)
    def test_move_upmost_up(self):
        r = self.c.post(reverse('ideaList.views.move_item'),
                {'item_id':self.i1.id, 'where':'up'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i1.id).position, 0)
        self.assertEqual(Item.objects.get(pk=self.i2.id).position, 1)
        self.check_state_in_response(r)
    def test_move_down(self):
        r = self.c.post(reverse('ideaList.views.move_item'),
                {'item_id':self.i2.id, 'where':'down'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i2.id).position, 2)
        self.assertEqual(Item.objects.get(pk=self.i3.id).position, 1)
        self.check_state_in_response(r)
    def test_move_down_across_trashed_item(self):
        self.i2.delete()
        r = self.c.post(reverse('ideaList.views.move_item'),
                {'item_id':self.i1.id, 'where':'down'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i1.id).position, 2)
        self.assertEqual(Item.objects.get(pk=self.i2.id).position, 0)
        self.assertEqual(Item.objects.get(pk=self.i3.id).position, 1)
        self.check_state_in_response(r)
    def test_move_up_across_trashed_item(self):
        self.i2.delete()
        r = self.c.post(reverse('ideaList.views.move_item'),
                {'item_id':self.i3.id, 'where':'up'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i1.id).position, 1)
        self.assertEqual(Item.objects.get(pk=self.i2.id).position, 2)
        self.assertEqual(Item.objects.get(pk=self.i3.id).position, 0)
        self.check_state_in_response(r)
    def test_move_abs(self):
        r = self.c.post(reverse('ideaList.views.move_item'),
                {'item_id':self.i1.id, 'where':2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i1.id).position, 2)
        self.assertEqual(Item.objects.get(pk=self.i2.id).position, 0)
        self.assertEqual(Item.objects.get(pk=self.i3.id).position, 1)
        self.check_state_in_response(r)

class EditTextViewTest(MyViewTest):
    def setUp(self):
        super(EditTextViewTest, self).setUp()
        u = User.objects.all()[0]
        self.l1 = List.objects.create(name='List1', owner=u)
        self.i1 = Item.objects.create(list=self.l1, text='testitem1')
        self.s1 = Subscription.objects.create(user=u, list=self.l1)
    def test_login_required(self):
        self.check_login_required('ideaList.views.edit_text')
    def test_valid_item_request(self):
        r = self.c.post(reverse('ideaList.views.edit_text'),
                {'element_id':'item_'+str(self.i1.id)+'_text', 'text':'lolo'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.get(pk=self.i1.id).text, 'lolo')
        data = self.check_state_in_response(r)
        self.assertIn('text', data)
        self.assertEqual(data['text'], 'lolo')
    def test_valid_list_request(self):
        r = self.c.post(reverse('ideaList.views.edit_text'),
                {'element_id':'subscription_'+str(self.s1.id)+'_listname',
                    'text':'wololo'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(List.objects.get(pk=self.l1.id).name, 'wololo')
        data = self.check_state_in_response(r)
        self.assertIn('text', data)
        self.assertEqual(data['text'], 'wololo')
    def test_element_id_missing(self):
        r = self.c.post(reverse('ideaList.views.edit_text'),
                {'text':'lolo'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.get(pk=self.i1.id).text, 'testitem1')
    def test_element_id_invalid(self):
        r = self.c.post(reverse('ideaList.views.edit_text'),
                {'element_id':'item_'+str(self.i1.id)+'_tex', 'text':'lolo'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.get(pk=self.i1.id).text, 'testitem1')
    def test_item_id_invalid(self):
        r = self.c.post(reverse('ideaList.views.edit_text'),
                {'element_id':'item_'+str(self.i1.id+1)+'_text', 'text':'lolo'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(Item.objects.get(pk=self.i1.id).text, 'testitem1')
    def test_text_missing(self):
        r = self.c.post(reverse('ideaList.views.edit_text'),
                {'element_id':'item_'+str(self.i1.id)+'_text'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.get(pk=self.i1.id).text, 'testitem1')


class AddListViewTest(MyViewTest):
    def setUp(self):
        super(AddListViewTest, self).setUp()
        self.assertEqual(List.objects.count(), 0)
    def test_login_required(self):
        self.check_login_required('ideaList.views.add_list')
    def test_add_list(self):
        r = self.c.post(reverse('ideaList.views.add_list'),
                {'name':'List1'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.check_state_in_response(r)
        self.assertEqual(List.objects.count(), 1)
    def test_add_list_and_subscribe(self):
        self.assertEqual(Subscription.objects.count(), 0)
        r = self.c.post(reverse('ideaList.views.add_list'),
                {'name':'List1', 'subscribe':'true'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.check_state_in_response(r)
        self.assertEqual(List.objects.count(), 1)
        l = List.objects.all()[0]
        self.assertEqual(l.name, 'List1')
        self.assertEqual(Subscription.objects.count(), 1)
        s = Subscription.objects.all()[0]
        self.assertEqual(s.list, l)
        self.assertEqual(s.user, self.u1)
    def test_add_list_with_misspelled_name(self):
        r = self.c.post(reverse('ideaList.views.add_list'),
                {'naem':'List1'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.check_state_in_response(r)
        self.assertEqual(List.objects.count(), 0)
    def test_add_list_with_empty_name(self):
        r = self.c.post(reverse('ideaList.views.add_list'),
                {'name':''},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        data = self.check_state_in_response(r)
        self.assertIn('msg', data)
        self.assertIn('empty', data['msg'])
        self.assertEqual(List.objects.count(), 0)

class RemoveListViewTest(MyViewTest):
    def setUp(self):
        super(RemoveListViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=self.u1)
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.nontrash.count(), 1)
    def test_login_required(self):
        self.check_login_required('ideaList.views.remove_list')
    def test_remove_list(self):
        r = self.c.post(reverse('ideaList.views.remove_list'),
                {'list_id':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.check_state_in_response(r)
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.nontrash.count(), 0)
    def test_remove_list_with_missing_id(self):
        r = self.c.post(reverse('ideaList.views.remove_list'),
                {'list_idd':self.l1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.check_state_in_response(r)
    def test_remove_list_with_invalid_id(self):
        r = self.c.post(reverse('ideaList.views.remove_list'),
                {'list_id':self.l1.id+1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.check_state_in_response(r)
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.nontrash.count(), 1)
