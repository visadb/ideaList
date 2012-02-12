from windmill.authoring import WindmillTestClient

def test_minimize_list():
    client = WindmillTestClient(__name__)

    client.asserts.assertJS(js=u"$('#subscription_1 > .itemlist').is(':visible')")
    client.asserts.assertJS(js=u"$('#itemcount_subscription_1').is(':hidden')")
    client.click(id=u'minmax_subscription_1')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#subscription_1 > .itemlist').is(':hidden')")
    client.asserts.assertJS(js=u"$('#itemcount_subscription_1').is(':visible')")
    client.asserts.assertJS(js=u'$(\'#itemcount_subscription_1 > .count\').html() == "0"')
    client.click(id=u'minmax_subscription_1')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#subscription_1 > .itemlist').is(':visible')")
    client.asserts.assertJS(js=u"$('#itemcount_subscription_1').is(':hidden')")
