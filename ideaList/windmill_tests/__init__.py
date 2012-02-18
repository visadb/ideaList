from windmill.authoring import WindmillTestClient

def setup_module(module):
    "Login and create three lists"
    client = WindmillTestClient(__name__)

    client.asserts.assertNode(id=u"id_username")
    client.type(text=u'visa', id=u'id_username')
    client.asserts.assertNode(id=u"id_password")
    client.type(text=u'salakala', id=u'id_password')
    client.click(value=u'login')
    client.waits.forPageLoad(timeout=u'20000')

    client.asserts.assertText(xpath=u"//div[@id='user-tools']/a", validator=u'Log out')
    client.execJS(js='window.autorefresh_freq = -1;')

    def create_list(i):
        name = 'test list '+str(i)
        client.asserts.assertNotNode(id=u"subscription_"+str(i))
        client.asserts.assertNode(id=u"create_list_nameinput")
        client.type(id=u'create_list_nameinput', text=name)
        client.keyUp(id=u'create_list_nameinput', options='13,false,false,false,false,false')
        client.waits.forElement(id=u"subscription_"+str(i), timeout=u'20000')

    client.asserts.assertJS(js=u"$('#listmenu_listlist').is(':hidden')")
    client.asserts.assertNode(id=u"lists_button")
    client.click(id=u"lists_button") # show list menu
    client.waits.sleep(milliseconds=u'500')
    client.asserts.assertNotJS(js=u"$('#listmenu_listlist').is(':hidden')")
    for i in [1,2,3]:
        create_list(i)
    client.click(id=u"lists_button") # hide list menu

def teardown_module(module):
    "Logout"
    client = WindmillTestClient(__name__)
    client = client # silence warning

    #client.click(link=u'Log out')
    #client.waits.forPageLoad(timeout=u'20000')
    #client.asserts.assertNode(name=u'username')
    #client.asserts.assertNode(name=u'password')

    #TODO: remove and purge lists (will also purge subscriptions and any remaining items)
