from windmill.authoring import WindmillTestClient

def test_move_item():
    client = WindmillTestClient(__name__)

    # show arrows
    client.asserts.assertJS(js=u"$('#move_item_1_up').is(':hidden')")
    client.click(id=u'more_button')
    client.waits.sleep(milliseconds=u'500')
    client.click(id=u'arrows_button') # Closes dropdown
    client.asserts.assertJS(js=u"$('#move_item_1_up').is(':visible')")

    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    client.click(id=u'move_item_1_up')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    client.click(id=u'move_item_1_down')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    client.click(id=u'move_item_2_up')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_3'")

    client.click(id=u'move_item_2_down')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    client.click(id=u'move_item_1_up')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")

    # hide arrows
    client.click(id=u'more_button')
    client.waits.sleep(milliseconds=u'500')
    client.click(id=u'arrows_button') # Closes dropdown
