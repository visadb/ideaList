from windmill.authoring import WindmillTestClient

def test_remove_list():
    client = WindmillTestClient(__name__)

    client.click(id=u"lists_button") # show list menu
    client.waits.sleep(milliseconds=u'500')

    #delete list
    client.asserts.assertNode(id=u"subscription_2")
    client.click(id=u"remove_list_2")
    client.waits.forNotElement(id=u"subscription_2", timeout=u'20000')

    #undelete list
    client.click(id=u"actions_button") # show list menu
    client.waits.sleep(milliseconds=u'500')
    client.click(link=u'Undelete items and lists')
    client.waits.forPageLoad(timeout=u'20000')
    client.check(xpath=u"//input[@name='list_ids' and @value='2']")
    client.click(name=u'undelete')
    client.waits.forPageLoad(timeout=u'20000')
    client.click(link=u'Back to main view')
    client.waits.forPageLoad(timeout=u'20000')
    client.asserts.assertNode(id=u"subscription_2")
