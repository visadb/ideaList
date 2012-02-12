from windmill.authoring import WindmillTestClient

def test_unsubscribe():
    client = WindmillTestClient(__name__)

    client.click(id=u"lists_button") # show list menu
    client.waits.sleep(milliseconds=u'500')

    #unsubscribe
    client.asserts.assertNode(id=u"subscription_2")
    client.asserts.assertNode(id=u"unsubscribe_list_2")
    client.click(id=u"unsubscribe_list_2")
    client.waits.forNotElement(id=u"subscription_2", timeout=u'20000')

    #subscribe
    client.waits.forElement(id=u"subscribe_list_2", timeout=u'20000')
    client.click(id=u"subscribe_list_2")
    client.waits.forElement(id=u"subscription_2", timeout=u'20000')
    client.click(id=u"lists_button") # hide list menu
