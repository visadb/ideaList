from windmill.authoring import WindmillTestClient

def test_drag_list():
    client = WindmillTestClient(__name__)

    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.dragDropElemToElem(optid=u'subscription_1', id=u'subscription_2')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.dragDropElemToElem(optid=u'subscription_2', id=u'subscription_3')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_3'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_1'")

    client.dragDropElemToElem(optxpath=u"//li[@id='subscription_1']/ul", id=u'subscription_3')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.dragDropElemToElem(optxpath=u"//li[@id='subscription_1']/ul", id=u'subscription_2')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")
