from windmill.authoring import WindmillTestClient

def test_toggle_item_importance():
    client = WindmillTestClient(__name__)

    # make item 3 important
    client.asserts.assertJS(js=u"$('#important_button').is(':hidden')")
    client.check(xpath=u"//li[@id='item_3']/input[@type='checkbox']")
    client.asserts.assertChecked(xpath=u"//li[@id='item_3']/input[@type='checkbox']")
    client.asserts.assertJS(js=u"$('#important_button').is(':visible')")
    client.asserts.assertNotJS(js=u"$('#item_3').hasClass('important')")
    client.click(id=u'important_button')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#item_3').hasClass('important')")
    client.asserts.assertJS(js=u"$('#remove_button').is(':hidden')")

    # toggle importance of 1 and 3
    client.check(xpath=u"//li[@id='item_1']/input[@type='checkbox']")
    client.asserts.assertChecked(xpath=u"//li[@id='item_1']/input[@type='checkbox']")
    client.check(xpath=u"//li[@id='item_3']/input[@type='checkbox']")
    client.asserts.assertChecked(xpath=u"//li[@id='item_3']/input[@type='checkbox']")
    client.asserts.assertNotJS(js=u"$('#item_1').hasClass('important')")
    client.click(id=u'important_button')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertJS(js=u"$('#item_1').hasClass('important')")
    client.asserts.assertNotJS(js=u"$('#item_3').hasClass('important')")

    # reset importance of 1
    client.check(xpath=u"//li[@id='item_1']/input[@type='checkbox']")
    client.asserts.assertChecked(xpath=u"//li[@id='item_1']/input[@type='checkbox']")
    client.click(id=u'important_button')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertNotJS(js=u"$('#item_1').hasClass('important')")
    client.asserts.assertNotJS(js=u"$('#item_3').hasClass('important')")
