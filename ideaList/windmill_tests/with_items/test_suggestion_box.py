from windmill.authoring import WindmillTestClient

def test_unsubscribe():
    client = WindmillTestClient(__name__)
    
    # Refresh to get the newest itemfrequencies
    client.refresh()

    # Add item from first suggestion
    client.asserts.assertNotNode(id=u'item_6')
    client.asserts.assertJS(js=u"$('#suggestion_box').is(':hidden')")
    client.click(xpath=u"//li[@id='item_3']/a[@title='Add item']")
    client.waits.sleep(milliseconds=u'50')
    client.asserts.assertJS(js=u"$('#suggestion_box').is(':visible')")
    client.asserts.assertNode(id=u"suggestion_0")
    client.click(id=u"suggestion_0")
    client.waits.forElement(id=u"item_6", timeout=u'20000')
    client.asserts.assertJS(js=u"$('#suggestion_box').is(':hidden')")

    #delete item
    client.asserts.assertJS(js=u"$('#remove_button').is(':hidden')")
    client.check(xpath=u"//li[@id='item_6']/input[@type='checkbox']")
    client.asserts.assertChecked(xpath=u"//li[@id='item_6']/input[@type='checkbox']")
    client.asserts.assertJS(js=u"$('#remove_button').is(':visible')")
    client.click(id=u'remove_button')
    client.waits.forNotElement(timeout=u'20000', id=u'item_6')
    client.asserts.assertJS(js=u"$('#remove_button').is(':hidden')")

    # purge item
    client.click(id=u'more_button')
    client.waits.sleep(milliseconds=u'500')
    client.click(link=u'Deleted stuff')
    client.waits.forPageLoad(timeout=u'20000')
    client.asserts.assertNode(xpath=u"//input[@name='item_ids' and @value='6']")
    client.check(xpath=u"//input[@name='item_ids' and @value='6']")
    client.asserts.assertChecked(xpath=u"//input[@name='item_ids' and @value='6']")
    client.click(name=u'purge')
    client.waits.forPageLoad(timeout=u'20000')
    client.asserts.assertNotNode(xpath=u"//input[@name='item_ids' and @value='6']")
    client.click(link=u'Back to main view')
    client.waits.forPageLoad(timeout=u'20000')
    client.asserts.assertNotNode(id=u'item_6')
