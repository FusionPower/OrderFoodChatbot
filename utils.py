from word2number import w2n
import json

def getAction(response, i):
    """
    Extract action from response
    """
    action = ""
    while response[i] in "0987654321":
        action += response[i]
        i+=1
    return int(action), i

def separateResponse(response):
    """
    Separate the actions from the completion
    """
    actions = []
    completion = ""
    response+=" "
    i=0
    while i<len(response):
        if response[i]=="," or response[i]==" ":
            i+=1
        elif response[i] in "0987654321":
            action, i = getAction(response, i)
            actions.append(action)
        else:
            completion = response[i:]
            break
    return actions, completion

def getSimilarity(lookupItem, menuItem, shingleSize):
    lookupItem = lookupItem.lower()
    menuItem = menuItem.lower()
    orderedItemShingles = [lookupItem[i:i+shingleSize] for i in range(len(lookupItem)-shingleSize+1)]
    menuItemShingles = [menuItem[i:i+shingleSize] for i in range(len(menuItem)-shingleSize+1)]

    numCommonShingles = 0
    for shingle in orderedItemShingles:
        if shingle in menuItemShingles:
            numCommonShingles += 1
    
    return numCommonShingles / (len(orderedItemShingles))

def isInDB(orderedItem, similarityThreshold=0.4, shingleSize=3):
    menu = json.load(open("menu.json", "r"))
    bestSimilarities = []
    for menu_item in menu.keys():
        similarity = getSimilarity(orderedItem, menu_item, shingleSize)
        if similarity > similarityThreshold:
            bestSimilarities.append([similarity, menu_item])
    if len(bestSimilarities)==0:
        return None
    bestSimilarities.sort()
    return bestSimilarities[-1][1]

def separateItem(item):
    """
    separate the number of food items from the food item
    """

    maxNumIndex = -1
    maxNum = -1
    for i in range(len(item)):
        try:
            if w2n.word_to_num(item[:i]) != maxNum:
                maxNum = w2n.word_to_num(item[:i])
                maxNumIndex = i                      
        except:
            pass

    amount = w2n.word_to_num(item[:maxNumIndex])
    food = item[maxNumIndex:]
    assert maxNumIndex != -1, "could not find amount of food in chat response"

    return int(amount), food
        

def getFoodItems(completion, action=None):
    """
    This function separates the food items from the completion string depending
    on the action that triggered the completion.
    """
    completion = completion.strip(".")
    completion = completion.replace("Your order is:", "")
    if action in [2,5]:
        foodItems = completion.split(", ")
    elif action == 4:
        foodItems = completion.replace("\n", "")
        foodItems = foodItems.split("//")
    for i,v in enumerate(foodItems):
        foodItems[i] = v.strip()
    return foodItems

def getCurrentOrder(order, askForConfirmation=True):
    if len(order)==0:
        response = "Your order is empty, what do you want to order?"
    else:
        response = "Your order is:\n"
        response += "\n".join(order)
        if askForConfirmation:
            response += "\nIs this correct?"
    return response

def getFieldAndFoodItem(request):
    """
    This function helps process menu queries.
    """
    request = request.strip(" ")
    request = request.strip(")")
    request = request.split("(")
    return request[0], request[1]
    
def findFoodInOrder(food, order):
    for i, orderItem in enumerate(order):
        similarFood = isInDB(food)
        similarOrderItem = isInDB(orderItem)
        if similarFood.lower() == similarOrderItem.lower():
            return i
    return -1

def changeOrderFoodcount(item, order, decrease = False, increase = False):

    if decrease and increase:
        assert False, "Cannot decrease and increase at the same time"
    if not decrease and not increase:
        assert False, "Must decrease or increase"

    amount, food = separateItem(item)
    if increase and not isInDB(food):
        return False

    orderIndex = findFoodInOrder(food, order)
    trueFoodName = isInDB(food)
    if orderIndex != -1:
        if decrease:
            orderItemAmountLeft = int(order[orderIndex][0])-amount
        elif increase:
            orderItemAmountLeft = int(order[orderIndex][0])+amount

        if orderItemAmountLeft <= 0:
            order.pop(orderIndex)
        else:
            order[orderIndex] = str(orderItemAmountLeft) + " " + trueFoodName
    elif increase and orderIndex == -1:
        order.append(str(amount) + " " + trueFoodName)
    return True
        
