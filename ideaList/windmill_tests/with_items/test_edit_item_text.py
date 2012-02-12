from windmill.authoring import WindmillTestClient

def test_edit_list_name():
    client = WindmillTestClient(__name__)

    client.asserts.assertNode(id=u'item_1_text')
    client.asserts.assertText(validator=u'test item 1', id=u'item_1_text')
    client.click(id=u'item_1_text')
    client.type(text=u'pim pom', name=u'text')
    client.keyPress(options=u'13,false,false,false,false,false', name=u'text')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertText(validator=u'pim pom', id=u'item_1_text')
    client.click(id=u'item_1_text')
    client.type(text=u'test item 1', name=u'text')
    client.keyPress(options=u'13,false,false,false,false,false', name=u'text')
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertText(validator=u'test item 1', id=u'item_1_text')
