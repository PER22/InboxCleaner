Inbox Cleaner
Author: Padraic Reilly

USE AT YOUR OWN RISK!

As an overview, InboxCleaner will assemble a list of messages that contain matching terms and delete them in bulk, to save you the time of searching then only being able to delete as many as display in the browser. Before they are actually deleted, you will be notified of the number, just to make sure you haven't made a fatal mistake. 

It needs the pip python package manager, googles authentication package, and python 2.7, as well as an active Gmail.com account. I will include a brief installation writeup below, but it is mostly copied from Googles own documentation.

InboxCleaner will, in the future, read files in of keywords to delete, and keywords to preserve, and ask for new ones, before assembling a list of messages and asking to proceed. At the end of the session, they will be saved.

For example, you could enter "CatFacts" to get rid of those pesky CatFacts messages that are sitting around your inbox. However, putting something in like "the" would have disastrous results.

It can also append the "from:" prefix to its terms if they are emails, to further specify which messages to delete. You might, for example, add "spammer@spam.com" to the list of emails to delete everything from, which would then be reformatted as "from:spammer@spam.com."

If you wanted to, for example, delete all the CatFacts that don't relate to your favorite Fact Cat named Mishka, then you could enter as a preserve keyword "Mishka", and any messages that contained "Mishka" will not be deleted, EVEN IF THEY MATCH DELETION PARAMETERS. Here is where your own knowledge of Google's search function can be applied. For example, you dont want deleted before a certain date, you can add the "before:yyyy/mm/dd" term by hand here. This is to give you as much flexibility as possible.  

If you wanted to get rid of all those pesky CatFacts, but your grandmother happens to sometimes include a CatFact for you, you can add her email "Granny@email.com" to the preservation keyword list, and it would be reformatted to "from:Granny@email.com". In that case, the CatFacts emails NOT from your grandmother will be deleted.

This is executed by using sets of message ID's and before user confirmation/deletion, the deletion set has the preservation set subtracted from it. No message ID that is in the PRESERVE list will be allowed to remain in the DELETE list.

This represents only a few hours work and has relatively few safeguards, so it goes without saying that this is to be used at your own risk. I am writing this as a personal excercise and a tool that I will probably only use a few times, carefully.

Feel free to submit issues, requests, fork this repo, or contact me personally at preil001@ucr.edu

