from windmill.authoring import WindmillTestClient

def test_edit_list_name():
    client = WindmillTestClient(__name__)

    client.asserts.assertNode(id=u'subscription_1_listname')
    client.asserts.assertText(validator=u'test list 1', id=u'subscription_1_listname')
    client.click(id=u'subscription_1_listname')
    client.type(text=u'shagalaga', name=u'text')
    client.keyPress(options=u'13,false,false,false,false,false', name=u'text')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertText(validator=u'shagalaga', id=u'subscription_1_listname')
    client.click(id=u'subscription_1_listname')
    client.type(text=u'test list 1', name=u'text')
    client.keyPress(options=u'13,false,false,false,false,false', name=u'text')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertText(validator=u'test list 1', id=u'subscription_1_listname')
