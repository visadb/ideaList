from windmill.authoring import WindmillTestClient

def test_drag_item():
    client = WindmillTestClient(__name__)

    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")

    # Within a single list:

    # Item 1 to last position
    client.dragDropElemToElem(id=u'item_1', optid=u'subscription_2')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_1'")
    # And back
    client.dragDropElemToElem(id=u'item_1', optid=u'item_4')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    # Item 4 to last position
    client.dragDropElemToElem(id=u'item_4', optid=u'subscription_2')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_4'")
    # And back
    client.dragDropElemToElem(id=u'item_4', optid=u'item_3')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    # Item 3 to top
    client.dragDropElemToElem(id=u'item_3', optid=u'item_1')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")
    # And back
    client.dragDropElemToElem(id=u'item_3', optid=u'item_2')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    # Between lists:

    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")

    # Item 1 to bottom of list 2
    client.dragDropElemToElem(id=u'item_1', optid=u'item_5')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(1)').attr('id') == 'item_1'")
    # And back
    client.dragDropElemToElem(id=u'item_1', optid=u'item_4')
    client.waits.sleep(milliseconds=u'600')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")

    # Item 1 to list 3 (empty)
    client.dragDropElemToElem(id=u'item_1', optxpath=u"//li[@id='subscription_3']/ul")
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")
    client.asserts.assertJS(js=u"$('#subscription_3 .item:nth(0)').attr('id') == 'item_1'")
    # And back
    client.dragDropElemToElem(id=u'item_1', optid=u'item_4')
    client.waits.sleep(milliseconds=u'600')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")
