from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from validate_email import validate_email
from apiclient import errors

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
###########################################################
def loadFileToSet(sourceFile, fileExtension, descriptor): 

    setOfKeys = set()
   #check file extensions, if ok, load the values into the delete kywds set
    if sourceFile.lower().endswith(fileExtension):
        try:
            filehandle = open(sourceFile,"r")
            for line in filehandle:
                if (line != "") and (line != " ") and (line != "\n"):
                    setOfKeys.add(line)
            filehandle.close()     
        except IOError:
            print("\nInvalid file. Proceeding without loading it. \n")
    else:
        print("\nInvalid file extension, be careful.\n")
    #ask if you want to remove any?, if yes, indicate which, remove, redisplay, and ask again
    user_input = ""
    print("\033c")
    while(user_input != "no") and (len(setOfKeys) > 0):
        #print delete kywds set
        for keywd in setOfKeys:
            print(keywd)
        user_input = raw_input("These are the " + str(descriptor) + " keywords. Do you want to remove any? no to continue, yes to select: ")
        if user_input == "yes":
            user_input = raw_input("Which one?    ")
            if (str(user_input)+ "\n") in setOfKeys:
                setOfKeys.remove(str(user_input) + "\n")
            else:
                print("Couldn't identify the term to delete.")
    return setOfKeys        
###########################################################
def main():
    #Google's OAuth2 code
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    #end of Google's code

    deleteKeywordsAndUsers = set()
    keepKeywordsAndUsers = set()
    user_input = ""
    delete_filename = "default.dltkeys"
    keep_filename = "default.kpkeys"
    
    #Ask to load from delete kywds file, should only be using delete* variables until otherwise stated.
    while (user_input != "yes") and (user_input != "no"):
        if user_input != "":
            print("Invalid response. Try again. \n\n")
        user_input = raw_input("Do you want to load delete keywords from the file?\nType yes or no: ")
    
    if user_input == "yes":
       
        #Get file name and verify.
        delete_filename = raw_input("\nEnter the name of your file. Delete Files should end in .dltkeys:   ")
        deleteKeywordsAndUsers |= loadFileToSet(delete_filename, "dltkeys", "delete")
    #Ask to load from preserve keywrods file, only use keep* variables until otherwise stated.  
    user_input = ""   
    while (user_input != "yes") and (user_input != "no"):
        if user_input != "":
            print("Invalid response. Try again. \n\n")
        user_input = raw_input("Do you want to load preservation keywords from the file?\nType yes or no: ")
    
    if user_input == "yes":
        #Get file name and verify.
        keep_filename = raw_input("\nEnter the name of your file. Keep key files should end in .kpkeys:   ")
        keepKeywordsAndUsers |= loadFileToSet(keep_filename, ".kpkeys", "preservation")
            
       
        
    #remove all preserve kywds from the list of delete kywds, in place so no accidents happen
    deleteKeywordsAndUsers -= keepKeywordsAndUsers

    #Collect new keywords from user
    deleteKeywordsAndUsers |= collectDeleteKeywordsAndUsers()
    keepKeywordsAndUsers |= collectKeepKeywordsAndUsers()
    
    #remove any mistakes again in the safest way possible
    deleteKeywordsAndUsers -= keepKeywordsAndUsers
    
    #clear screen and output the lists thus far
    print('\033c')
    print("Deletion keywords and addresses:\n")
    for each in deleteKeywordsAndUsers:
        print(each )
    print("\n\nKeeping messages that have these terms or addresses:\n\n")
    for each in keepKeywordsAndUsers:
        print(each)

    
    #Begin Collecting the Message IDs to delete via API call    
    setOfMessageIDsToDelete = set()
    setOfMessageIDsToKeep = set()
    #Collect all deleteable Message IDs
    for keyword in deleteKeywordsAndUsers:
        setOfMessageIDsToDelete |= setOfMessagesMatchingQuery(service, "me", keyword)
    #Collect all preservable Message IDs    
    for keyword in keepKeywordsAndUsers:
        setOfMessageIDsToKeep |= setOfMessagesMatchingQuery(service, "me", keyword)
    #Remove any messages that are in both in safest way possible
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
        deleteMessagesFromIDSet(setOfMessageIDsToDelete)
    else: 
        print("Deletion Cancelled.")

    
    user_input = ""
    user_input = raw_input("Do you want to save the changes you made to the delete keyword file? Type save, or any key to continue without saving.    ")
    if user_input == "save":
        saveSetToFile(deleteKeywordsAndUsers, delete_filename)
    
    user_input = ""
    user_input = raw_input("Do you want to save the changes you made to the preserve keyword file? Type save, or any key to continue without saving.   ")
    if user_input == "save":
        saveSetToFile(keepKeywordsAndUsers, keep_filename)
#####################################################################################
def deleteMessagesFromIDSet(setOfIDs):
    j = 0
    i = len(setOfIDs)
    for each in setOfIDs:
        print('\033c')
        try:
#CURRENTLY IN SAFE MODE                service.users().messages().trash(id=each, userId="me").execute()
            j+=1
            print("Deleted " + str(j)+ " / " + str(i) + "messages.\n" + str((i/j)*100) + "% complete.")


        except errors.HttpError, error:
            print("An error occured: "+ str(error))


#####################################################################################

def saveSetToFile(setToSave, fileToSaveIn):
    filehandle = open(fileToSaveIn, "w")
    for keywd in setToSave:
        filehandle.write(keywd + "\n") 
    filehandle.close()
#####################################################################################
        

def collectDeleteKeywordsAndUsers():
    setOfKeywordsAndUsers = set()
    userInput = ""
    while userInput != "q!":
        userInput = raw_input("Enter a keyword to add to delete list, or type q! to exit\n")
        if (userInput != "q!") and (userInput != "") and (userInput != " ") and (userInput != "\n") :
            setOfKeywordsAndUsers.add(userInput)
    userInput = ""
    print("\n\n")
    while userInput != "q!":
        userInput = raw_input("Enter any email addresses you want EVERYTHING deleted from:\n")
        
        if (userInput != "q!") and (userInput != "") and (userInput != " ") and (userInput != "\n") :
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
        
        if (userInput != "q!") and (userInput != "") and (userInput != " ") and (userInput != "\n") :
            setOfKeywordsAndUsers.add(userInput)
    userInput = ""
    print("\n\n")
    while userInput != "q!":
        userInput = raw_input("Enter an email address to NOT delete messages from (eg Grandma@gmail.com)\n")
        
        if (userInput != "q!") and (userInput != "") and (userInput != " ") and (userInput != "\n") :
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
