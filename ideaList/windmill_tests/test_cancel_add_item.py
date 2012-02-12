from windmill.authoring import WindmillTestClient

def test_cancel_add_item():
    client = WindmillTestClient(__name__)

    client.click(id=u'additem_list_1')
    client.asserts.assertNode(id=u'add_to_begin_of_list_1')
    client.click(xpath=u"//li[@id='subscription_1']/ul/li/a[@title='cancel']")
    client.waits.forNotElement(timeout=u'20000', id=u'add_to_begin_of_list_1')
