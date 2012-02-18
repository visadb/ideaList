from windmill.authoring import WindmillTestClient

def test_move_list():
    client = WindmillTestClient(__name__)

    # show arrows
    client.click(id=u'more_button')
    client.waits.sleep(milliseconds=u'500')
    client.click(id=u'arrows_button') # Closes dropdown

    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.click(id=u'move_subscription_1_up')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.click(id=u'move_subscription_2_up')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.click(id=u'move_subscription_1_down')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_3'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_1'")

    client.click(id=u'move_subscription_3_down')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    client.click(id=u'move_subscription_2_down')
    client.waits.sleep(milliseconds=u'200')
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(0)').attr('id') == 'subscription_1'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(1)').attr('id') == 'subscription_2'")
    client.asserts.assertJS(js=u"$('#listlist > .subscription:nth(2)').attr('id') == 'subscription_3'")

    # hide arrows
    client.click(id=u'more_button')
    client.waits.sleep(milliseconds=u'500')
    client.click(id=u'arrows_button') # Closes dropdown
