import json
from django import test
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ideaList.models import List, Item

class MyViewTest(test.TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        self.c = Client()
        self.assertTrue(self.c.login(username='visa', password='salakala'))
    def check_login_required(self, viewname):
        self.c.logout()
        r = self.c.get(reverse(viewname))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.has_header('Location'))
        self.assertTrue(reverse('django.contrib.auth.views.login') in
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

class AdditemViewTest(MyViewTest):
    def setUp(self):
        super(AdditemViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=User.objects.all()[0])
    def test_login_required(self):
        self.check_login_required('ideaList.views.additem')
    def test_valid_item(self):
        self.assertEqual(Item.objects.count(), 0)
        r = self.c.post(reverse('ideaList.views.additem'),
                {'list':self.l1.id, 'text':'Cheese', 'position':0},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 1)
        self.check_state_in_response(r)
        i = Item.objects.all()[0]
        self.assertEqual(i.list.id, self.l1.id)
        self.assertEqual(i.text, 'Cheese')
        self.assertEqual(i.position, 0)
    def test_invalid_list_id(self):
        self.assertEqual(Item.objects.count(), 0)
        r = self.c.post(reverse('ideaList.views.additem'),
                {'list':self.l1.id+5, 'text':'Cheese', 'position':0},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.count(), 0)
        self.check_state_in_response(r)
    def test_invalid_missing_position(self):
        self.assertEqual(Item.objects.count(), 0)
        r = self.c.post(reverse('ideaList.views.additem'),
                {'list':self.l1.id, 'text':'Cheese'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.count(), 0)

class RemoveitemViewTest(MyViewTest):
    def setUp(self):
        super(RemoveitemViewTest, self).setUp()
        self.l1 = List.objects.create(name='List1', owner=User.objects.all()[0])
        self.i1 = Item.objects.create(list=self.l1, text='testitem')
    def test_login_required(self):
        self.check_login_required('ideaList.views.removeitem')
    def test_valid_item_id(self):
        self.assertEqual(Item.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.removeitem'),
                {'item_id':self.i1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.trash.count(), 1)
        self.assertEqual(Item.nontrash.count(), 0)
        self.check_state_in_response(r)
    def test_item_id_missing(self):
        self.assertEqual(Item.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.removeitem'),
                {'item_id_mispelled':self.i1.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.count(), 1)
        self.check_state_in_response(r)
    def test_invalid_item_id(self):
        self.assertEqual(Item.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.removeitem'),
                {'item_id':'invalid'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Item.objects.count(), 1)
        self.check_state_in_response(r)
    def test_nonexisting_item_id(self):
        self.assertEqual(Item.objects.count(), 1)
        r = self.c.post(reverse('ideaList.views.removeitem'),
                {'item_id':self.i1.id+1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(Item.objects.count(), 1)
        self.check_state_in_response(r)
