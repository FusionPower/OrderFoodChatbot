"""
This file handles all the main functions to process a response from the model.
The fucntion processResponse handles all the function calls.

The functions use some utilities to help them out, which are in utils.py
"""


from utils import *


def converse(**kwargs):
    return kwargs["completion"], kwargs["order"]

def greet(**kwargs):
    return kwargs["completion"], kwargs["order"]

def addItems(**kwargs):
    """
    Add items to the order and read it back for confirmation
    """
    completion = kwargs["completion"]
    order = kwargs["order"]
    action = kwargs["action"]

    foodItems = getFoodItems(completion, action)
    foodNotInDB = []
    for item in foodItems:
        _, food = separateItem(item)
        if not changeOrderFoodcount(item, order, increase = True):
            foodNotInDB +=[food]
    

    response = getCurrentOrder(order)
    if len(foodNotInDB) > 0:
        itemsNotFound = "Sorry, we don't have the following items:\n" 
        itemsNotFound += "\n".join(foodNotInDB)
        itemsNotFound += "\n"
        response = itemsNotFound + response
    return response, order

def readOrder(**kwargs):
    return getCurrentOrder(kwargs["order"]), kwargs["order"]


def updateItem(**kwargs):
    """
    Update items in the order and read it back for confirmation
    """
    # TODO add sorry message for unfound items
    completion = kwargs["completion"]
    order = kwargs["order"]
    foodItems = getFoodItems(completion, kwargs["action"])
    assert len(foodItems)%2 == 0, "Update must have an item to update and a new item, but there are an odd number of items in the completion"

    for i in range(0, len(foodItems), 2):
        itemToReplace = foodItems[i]
        itemToReplaceWith = foodItems[i+1]

        changeOrderFoodcount(itemToReplace, order, decrease=True)
        changeOrderFoodcount(itemToReplaceWith, order, increase=True)
    
    response = getCurrentOrder(order)
    return response, order

def deleteItem(**kwargs):
    """
    Delete items from the order and read it back for confirmation
    """
    completion = kwargs["completion"]
    order = kwargs["order"]

    foodItems = getFoodItems(completion, kwargs["action"])

    for deleteItem in foodItems:
        changeOrderFoodcount(deleteItem, order, decrease = True)

    if len(order)==0:
        return "Your order is now empty", order
    response = getCurrentOrder(order)
    return response, order

def queryMenu(**kwargs):
    """
    Query the meny to get specifications about food. 
    You should be able to make more than one query at the time.
    Ingredient, price, gluten free, vegetarian queries supported
    """

    # TODO add queries for all items
    completion = kwargs["completion"]
    requests = completion.split(", ")
    response = ""
    menu = json.load(open("menu.json", "r"))

    for request in requests:
        request = request.strip()
        field, foodItem = getFieldAndFoodItem(request)
        lookupSuccessful = False
        trueFoodName = isInDB(foodItem)
        if trueFoodName!=None:
            try:
                if type(menu[trueFoodName][field]) in [float, int]:
                    response += trueFoodName + " is " + str(menu[trueFoodName][field])
                elif type(menu[trueFoodName][field]) == list:
                    response += trueFoodName + " has " + ", ".join(menu[trueFoodName][field])
                elif menu[trueFoodName][field] == True:
                    response += trueFoodName + " is " + field.replace("_", " ")
                elif menu[trueFoodName][field] == False:
                    response += trueFoodName + " is not " + field.replace("_", " ")
                response += "\n"
                lookupSuccessful = True
            except:
                pass
        if not lookupSuccessful:
            response += "Sorry, we don't have that information\n"
    response += "Do you want to add anything?\n"
    return response, kwargs["order"]

def subItemConfig(**kwargs):
    # TODO
    return kwargs["completion"], kwargs["order"]

def affirmative(**kwargs):
    """
    User confirmed an answer and depending what they confirmed to, we ask for more information.
    This could be separated into more classes by saving previous prompts and responses.
    """
    actionHistory = kwargs["actionHistory"]
    if 2 in actionHistory[-1] or 3 in actionHistory[-1] or 4 in actionHistory[-1]:
        return "Would you like anything else?", kwargs["order"]
    if 8 in actionHistory[-1]:
        return "Great! What else would you like?", kwargs["order"]
    else:
        return "I'm sorry, I didn't get that", kwargs["order"]
     

def negative(**kwargs):
    """
    User negated an answer and depending what they said no to, we undo the changes or ask
    for more info.

    This could be separated into more classes by saving previous prompts and responses.
    """
    actionHistory = kwargs["actionHistory"]
    if 2 in actionHistory[-1]:
        if len(kwargs["orderHistory"][-1])>0 and len(kwargs["orderHistory"])>1:
            return "Sorry, I'll undo the changes", kwargs["orderHistory"][-2][:]
        else:
            return "I'm sorry, I didn't get that", []
    if 6 in actionHistory[-1] or 8 in actionHistory[-1]:
        return "Okay, have a nice day", kwargs["order"]
    else:
        return "I'm sorry, I didn't get that", kwargs["order"]



def processResponse(response, actionHistory, orderHistory):
    """
    orderHistory and actionHistory are saved for possible uses in the future.
    They also help for rollbacks now.

    Completion has Items, which generally have amount and food
    """
    currentOrder = orderHistory[-1][:] if len(orderHistory)>0 else []
    iterationActions, completion = separateResponse(response)
    possibleActions = [
        converse, 
        greet,
        addItems, 
        readOrder, 
        updateItem, 
        deleteItem, 
        queryMenu, 
        subItemConfig, 
        affirmative, 
        negative
    ]

    # fine tunning generates only one action, handling of more actions should be implemented here
    for action in iterationActions:
        botMessage, currentOrder = possibleActions[action](
            completion=completion, 
            order=currentOrder, 
            orderHistory=orderHistory, 
            action=action, 
            actionHistory=actionHistory
        )
    assert len(iterationActions)>0, (f"No actions found completion: {completion}")
    orderHistory.append(currentOrder)
    actionHistory.append(iterationActions)
    return botMessage


