// Add this to AWS console (Ireland!!!) and put the arn to skill.json
// Then add Alexa Skills Kit trigger to lambda in console and add
// skill id to restrict access
// (get skill id from https://developer.amazon.com/alexa -> Your Alexa Consoles -> Skills)

const url = require('url')
const https = require('https')
const querystring = require('querystring')

const alexaListIdToIdeaListListId = {
    'YW16bjEuYWNjb3VudC5BR01UTUtVS1ZWNldMUFNXRFZRN0dDV1RaQkxBLVNIT1BQSU5HX0lURU0=': 1, // Shopping list <-> Ruokakauppa
    'c6ec5e22-0fcc-493b-8c05-67ffd5665b1d': 7, // Hardware <-> Tavarat
    'd3d7ed42-ac87-4063-9c5c-cc351cd2b59d': 2, // Pharmacy <-> Apteekki
    'YW16bjEuYWNjb3VudC5BR01UTUtVS1ZWNldMUFNXRFZRN0dDV1RaQkxBLVRBU0s=': 67, // To-do <-> TODO
}

exports.handler = async (event, context) => {
    console.log("Jevent", JSON.stringify(event, null, 2))
    const listId = event.request.body.listId
    const listItemId = event.request.body.listItemIds[0]
    const apiAccessToken = event.context.System.apiAccessToken
    const alexaApiHost = url.parse(event.context.System.apiEndpoint).host

    return new Promise((resolve, reject) => {
        if (event.request.type !== 'AlexaHouseholdListEvent.ItemsCreated') {
            reject('Unsupported request type ' + event.request.type)
        }

        const getItemOptions = {
            host: alexaApiHost,
            path: `/v2/householdlists/${listId}/items/${listItemId}`,
            headers: {
                "Authorization": `Bearer ${apiAccessToken}`
            }
        }

        https.get(getItemOptions, res => {
            let itemData = ''
            res.on('data', (chunk) => {
                itemData += chunk
            })
            res.on('end', () => {
                const item = JSON.parse(itemData)
                console.log("Got dada", JSON.stringify(item, null, 2))

                const postData = querystring.encode({
                    list: alexaListIdToIdeaListListId[listId] || 1,
                    text: item.value,
                    position: 0
                })
                const postToIdeaListOptions = {
                    method: 'POST',
                    hostname: 'vdb.re',
                    path: '/d/ideaList/alexa/AEKA5AEFAHHEEJA6HEI7/add_item/',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Content-Length': postData.length
                    }
                }
                const postToIdeaListReq = https.request(postToIdeaListOptions, res => {
                    console.log(`Posted ${postData} to ideaList, statusCode=${res.statusCode}`)

                    const deleteFromAlexaList = {
                        method: 'DELETE',
                        host: alexaApiHost,
                        path: `/v2/householdlists/${listId}/items/${listItemId}`,
                        headers: {
                            "Authorization": `Bearer ${apiAccessToken}`
                        }
                    }
                    const deleteFromAlexaListReq = https.request(deleteFromAlexaList, res => {
                        console.log(`Deleted ${listItemId} from Alexa list ${listId}, statusCode=${res.statusCode}`)
                        let deleteResponseBody = ''
                        res.on('data', chunk => {
                            deleteResponseBody += chunk
                        })
                        res.on('end', () => {
                            console.log("Delete response body", deleteResponseBody)
                            resolve('Jesh')
                        })

                    })
                    deleteFromAlexaListReq.on('error', (err) => {
                        console.log("Failed to delete item: " + err)
                        resolve("Failed to delete item: " + err) // ignore error on delete
                    })
                    deleteFromAlexaListReq.end()


                })
                postToIdeaListReq.on('error', e => {
                    console.log('Error posting to ideaList', e)
                    reject('Error posting to ideaList ' + e)
                })

                postToIdeaListReq.write(postData)
                postToIdeaListReq.end()
            })

        }).on('error', (err) => {
            console.log("Failed to get item: " + err)
            reject("Failed to get item: " + err)
        })
    })
}

