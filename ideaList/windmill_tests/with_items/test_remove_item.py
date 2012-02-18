from windmill.authoring import WindmillTestClient

def test_remove_item():
    client = WindmillTestClient(__name__)

    #delete
    client.asserts.assertJS(js=u"$('#remove_button').is(':hidden')")
    client.check(xpath=u"//li[@id='item_3']/input[@type='checkbox']")
    client.asserts.assertChecked(xpath=u"//li[@id='item_3']/input[@type='checkbox']")
    client.asserts.assertJS(js=u"$('#remove_button').is(':visible')")
    client.click(id=u'remove_button')
    client.waits.forNotElement(timeout=u'20000', id=u'item_3')
    client.asserts.assertJS(js=u"$('#remove_button').is(':hidden')")

    #undelete
    client.click(id=u'more_button')
    client.waits.sleep(milliseconds=u'500')
    client.click(link=u'Deleted stuff')
    client.waits.forPageLoad(timeout=u'20000')
    client.check(xpath=u"//input[@name='item_ids' and @value='3']")
    client.asserts.assertChecked(xpath=u"//input[@name='item_ids' and @value='3']")
    client.click(name=u'undelete')
    client.waits.forPageLoad(timeout=u'20000')
    client.click(link=u'Back to main view')
    client.waits.forPageLoad(timeout=u'20000')
    client.asserts.assertNode(id=u'item_3')
