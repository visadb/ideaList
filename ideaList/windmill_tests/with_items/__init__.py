from windmill.authoring import WindmillTestClient

def setup_module(module):
    "Add items. Also test suggestion box."
    client = WindmillTestClient(__name__)

    def enter_item_text(text, ctrl=False):
        if ctrl:
            options = u'13,false,true,false,false,false'
        else:
            options = u'13,false,false,false,false,false'
        client.waits.forElement(xpath=u"//input[@class='additem']", timeout=u'20000')
        client.type(xpath=u"//input[@class='additem']", text=text)
        client.keyUp(xpath=u"//input[@class='additem']", options=options)
        if not ctrl:
            client.waits.forNotElement(xpath=u"//input[@class='additem']", timeout=u'20000')

    client.asserts.assertNotNode(xpath=u"//input[@class='additem']")

    # 1st item to test list 1 (from list's additem button)
    client.asserts.assertNotNode(id=u'item_1')
    client.click(id=u'additem_list_1')
    enter_item_text('test item 1')
    client.waits.forElement(id=u"item_1", timeout=u'20000')

    # 2nd item to test list 1 (from item1's additem button)
    client.asserts.assertNotNode(id=u'item_2')
    client.click(xpath=u"//li[@id='item_1']/a[@title='Add item']")
    enter_item_text('test item 2')
    client.waits.forElement(id=u"item_2", timeout=u'20000')

    # 3rd item to test list 1 (from item1's additem button with ctrl)
    client.asserts.assertNotNode(id=u'item_3')
    client.click(xpath=u"//li[@id='item_1']/a[@title='Add item']")
    enter_item_text('test item 3', ctrl=True)
    client.waits.forElement(id=u"item_3", timeout=u'20000')

    # 4th item to test list 1 (with residual additem field from last one)
    client.asserts.assertNotNode(id=u'item_4')
    enter_item_text('test item 4')
    client.waits.forElement(id=u"item_4", timeout=u'20000')

    # 5th item to test list 2
    client.asserts.assertNotNode(id=u'item_5')
    client.click(id=u'additem_list_2')
    client.waits.sleep(milliseconds=u'50')
    client.asserts.assertJS(js=u"$('#suggestion_box').is(':hidden')")
    enter_item_text('test item 5')
    client.waits.forElement(id=u"item_5", timeout=u'20000')

    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(0)').attr('id') == 'item_1'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(1)').attr('id') == 'item_4'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(2)').attr('id') == 'item_3'")
    client.asserts.assertJS(js=u"$('#subscription_1 .item:nth(3)').attr('id') == 'item_2'")
    client.asserts.assertJS(js=u"$('#subscription_2 .item:nth(0)').attr('id') == 'item_5'")


def teardown_module(module):
    "Logout"
    client = WindmillTestClient(__name__)
    client = client # silence warning

    #TODO: remove and purge items
