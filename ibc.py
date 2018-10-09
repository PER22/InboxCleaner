from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from validate_email import validate_email
from apiclient import errors

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

def main():
    #Google's OAuth2 code
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    #Move keyword storage variables up here

    #Ask to load from delete kywds file
    #check file extensions, if ok, load the values into the delete kywds set
    #print delete kywds set
    #ask if you want to remove any?, if yes, indicate which and ask again

    #ask to load from preserve kywds file
    #check extensions, if ok load values into preserve kywds set
    #print preserve keywds set
    #ask if you want to remove any, if yes indicate which and ask again

    #remove all preserve kywds from the list of delete kywds, in place so no accidents happen

    
    

    #Collect new keywords from user
    deleteKeywordsAndUsers = collectDeleteKeywordsAndUsers()
    keepKeywordsAndUsers = collectKeepKeywordsAndUsers()
    #remove any mistakes in the safest way possible
    deleteKeywordsAndUsers -= keepKeywordsAndUsers
    #clear screen and output the lists thus far
    print('\033c')
    print("Deletion keywords and addresses:\n")
    for each in deleteKeywordsAndUsers:
        print(each )
    print("Keeping messages that have these terms or addresses:\n")
    for each in keepKeywordsAndUsers:
        print(each)

    #Ask if user would like to save either file with the added terms
    #if so, save by overwiting, and put the whole list back in.
    
    #Begin Collecting the Message IDs to delete via API call    
    setOfMessageIDsToDelete = set()
    setOfMessageIDsToKeep = set()
    #Collect all deleteable Message IDs
    for keyword in deleteKeywordsAndUsers:
        setOfMessageIDsToDelete |= setOfMessagesMatchingQuery(service, "me", keyword)
    #Collect all preservable Message IDs    
    for keyword in keepKeywordsAndUsers:
        setOfMessageIDsToKeep |= setOfMessagesMatchingQuery(service, "me", keyword)
    #Remove any duplicates in safest way possible
    setOfMessageIDsToDelete -= setOfMessageIDsToKeep
    #declare a variable to count them and make a readable output
    i = 0
    for msg in setOfMessageIDsToDelete:
        i+=1
        print(str(i) + ". "+ str(msg)) 

    #Confirm And Warn User     
    user_accept = ""
    while (user_accept != "DELETE") and (user_accept != "CANCEL"):
        if user_accept != "":
            print("\n\nInvalid response. Try again.")
        user_accept = raw_input("You are about to delete " + str(i ) + " messages.\n This could be a large inconvenience if you've made a mistake.\nType DELETE to continue or CANCEL to cancel: ")

    if user_accept == "DELETE":
        #Do a thing to delete them
        j = 0
        for each in setOfMessageIDsToDelete:
            print('\033c')
            try:
                service.users().messages().trash(id=each, userId="me").execute()
                j+=1
                print("Deleted " + str(j)+ " / " + str(i) + "messages.\n" + str((i/j)*100) + "% complete.")


            except errors.HttpError, error:
                print("An error occured: "+ str(error))
    else: 
        quit()
#####################################################################################
        

def collectDeleteKeywordsAndUsers():
    setOfKeywordsAndUsers = set()
    userInput = ""
    while userInput != "q!":
        userInput = raw_input("Enter a keyword to add to delete list, or type q! to exit\n")
        if userInput != "q!":
            setOfKeywordsAndUsers.add(userInput)
    userInput = ""
    print("\n\n")
    while userInput != "q!":
        userInput = raw_input("Enter any email addresses you want EVERYTHING deleted from:\n")
        if userInput != "q!":
            if validate_email(userInput):
                setOfKeywordsAndUsers.add("from:" + userInput)
            else: 
                print("Invalid email format. Try again. \n")    

    print("\n\n")

   # for item in setOfKeywordsAndUsers:
    #    print(item)
    return setOfKeywordsAndUsers

######################################################################################


def collectKeepKeywordsAndUsers():
    setOfKeywordsAndUsers = set()
    userInput = ""
    while userInput != "q!":
        userInput = raw_input("Enter a keyword to NOT delete (eg 'Order' or 'Invoice')\n")
        if userInput != "q!":
            setOfKeywordsAndUsers.add(userInput)
    userInput = ""
    print("\n\n")
    while userInput != "q!":
        userInput = raw_input("Enter an email address to NOT delete messages from (eg Grandma@gmail.com)\n")
        if userInput != "q!":
            if validate_email(userInput):
                setOfKeywordsAndUsers.add("from:" + userInput)
            else: 
                print("Invalid email format. Try again.\n")
    return setOfKeywordsAndUsers
########################################################################################
def setOfMessagesMatchingQuery(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id,q=query).execute()
        messages = []
        messageIDSet = set()
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                             pageToken=page_token).execute()
            messages.extend(response['messages'])

#        return set(messages)
#        print(messages)
        for each in messages:
            messageIDSet.add(each['id'])
        return messageIDSet    
    except errors.HttpError, error:
            print( 'An error occurred: '+ error + "\n\n")

########################################################################################

if __name__ == '__main__':
        main()
