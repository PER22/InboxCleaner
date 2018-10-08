from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from validate_email import validate_email
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
                print('No labels found.')
    else:
                print('Labels:')
                for label in labels:
                        print(label['name'])
    deleteKeywordsAndUsers = collectDeleteKeywordsAndUsers()
    keepKeywordsAndUsers = collectKeepKeywordsAndUsers()
    deleteKeywordsAndUsers -= keepKeywordsAndUsers
    print('\033c')
    print("Deletion keywords and addresses:\n")
    for each in deleteKeywordsAndUsers:
        print(each )
    print("Keeping messages that have these terms or addresses:\n")
    for each in keepKeywordsAndUsers:
        print(each)


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

if __name__ == '__main__':
        main()
