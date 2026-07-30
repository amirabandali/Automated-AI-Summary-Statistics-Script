"""python script to automate summarizing an article and showing reading time saved 
   by summary with use of python, google gemini, and powerBI"""

#global variables
articleCount = 0
fileNum = 1

#get article url from user
def userInput():
    article = input("Please paste the url of the article you would like to be analyzed: ")
    return article

from newspaper import Article

#retrieving article text from url
def retrieveArticle(article):
    n = Article(article)
    n.download()
    n.parse()
    return n.text

#allow files to be saved to users downloads
import os
downloads = os.path.join(os.path.expanduser("~"), "Downloads")

#importing groq ai
#utlizes groq ai api key to access groq ai models for summarization
from groq import Groq
client = Groq(api_key="Inset your API key here")

#to get summary as a paragraph 
def summaryParagraph(articleText):
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": (articleText + " Please summarize this article text into a concise paragraph."),
        }
    ],
    model="llama-3.3-70b-versatile",
)
    return chat_completion

#to get summary as bullet notes
def summaryBullet(articleText):
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": (articleText + " Please summarize this article text into concise bullet notes."),
        }
    ],
    model="llama-3.3-70b-versatile",  
)
    return chat_completion

#to ask whether user wants bullet notes or paragraph
def inputSummary():
    format = input("Would you like the article summary to be in a) paragraph or b) bullet note format? Please type a or b and press enter: ")
    return format

#redirect to functions based on users preference of summary
def getSummary(summaryType, articleText):
    message = None
    while message == None:
        if summaryType.strip().lower() == "a":
            message = summaryParagraph(articleText)
            return message

        elif summaryType.strip().lower() == "b":
            message = summaryBullet(articleText)
            return message

        else:
            print("Sorry, that is not a valid response.")
            summaryType = input("Would you like the article summary to be in a) paragraph or b) bullet note format? Please type a or b and press enter: ")

#display on powerBI via csv files
import pandas as pd

#retrieving statistics to display
def getStats(articleInput, articleText, summary):
    original_words = len(articleText.split())
    summary_words = len(summary.split())

    reading_rate = 200

    original_time = original_words / reading_rate
    summary_time = summary_words / reading_rate

    time_saved = original_time - summary_time

    n = Article(articleInput)
    n.download()
    n.parse()

    data = [
        [n.title + " Article", original_words, original_time],
        [n.title + " AI Summary", summary_words, summary_time]
    ]

    articleAnalysis = pd.DataFrame(
        data,
        columns=["Text", "Word Count", "Reading Time (mins)"]
    )

    if articleCount == 0:
        articleAnalysis.to_csv(os.path.join(downloads, "Article_Analysis.csv"), index=False)

    #how user would like to save statistics if this isn't their first usage
    if articleCount >= 1:
        dataCumulativeSave = None
        while dataCumulativeSave == None:
            dataCumulativeSave = input("Would you like the new article statistics to a) overwrite the previous article statistics you asked for, b) be appended to the same csv file, or c) written in a new csv file? Please type a, b, or c and press enter: ")

            if dataCumulativeSave.strip().lower() == "a":
                articleAnalysis.to_csv(os.path.join(downloads, "Article_Analysis.csv"), index=False)
            
            elif dataCumulativeSave.strip().lower() == "b":
                articleAnalysis.to_csv(os.path.join(downloads, "Article_Analysis.csv"), index=False)
            
            elif dataCumulativeSave.strip().lower() == "c":
                articleAnalysis.to_csv(os.path.join(downloads, f"Article_Analysis{fileNum}.csv"), index=False)

            else:
                print("Sorry that is not a valid response.")

#function to put together all functions
def runCode():
    #user input for article
    articleInput = userInput()
    articleText = retrieveArticle(articleInput)

    #AI summary
    summaryType = inputSummary()
    summaryFinal = getSummary(summaryType, articleText)

    #reading stats
    summary = summaryFinal.choices[0].message.content
    getStats(articleInput, articleText, summary)

    return summary

#variable for user input error
redo = True

#to see if user would like to analyze another article
if articleCount == 0:
    savedSummary = runCode()
    with open(os.path.join(downloads, "Article_Summary.txt") , "w" , encoding="utf-8") as file:
        file.write(savedSummary)
    print("File Saved. Statistics Updated.")
    articleCount = 1
    repeat = input("Would you like to analyze another article? Please type yes or no and press enter: ")
    if repeat.strip().lower() == "yes":
        articleCount = articleCount + 1
    while repeat.strip().lower() != "yes" and repeat != "no":
        print("Sorry, that is not a valid response")
        repeat = input("Would you like to analyze another article? Please type yes or no and press enter: ")
    if repeat.strip().lower() == "no": 
        redo = False
    
#variable for options of saving the summary txt file
cumulativeSave = "None"

##to see how users would like to save the article - choices if this isn't their first usage
while repeat.strip().lower() == "yes" or redo == True:
    if articleCount >= 1:
        savedSummary = runCode()

        while cumulativeSave == "None":
            cumulativeSave = input("Would you like the new article summary to a) overwrite the previous article summary you asked for, b) be appended to the same txt file, or c) written in a new txt file? Please type a, b, or c and press enter: ")

            if cumulativeSave.strip().lower() == "a":
                with open(os.path.join(downloads, "Article_Summary.txt"), "w" , encoding="utf-8") as file:
                    file.write(savedSummary)
                print("File Saved. Statistics Updated.")

            elif cumulativeSave.strip().lower() == "b":
                with open(os.path.join(downloads, "Article_Summary.txt"), "a" , encoding="utf-8") as file:
                    file.write("\n" + savedSummary)
                print("File Saved. Statistics Updated.")

            elif cumulativeSave.strip().lower() == "c":
                with open(os.path.join(downloads, f"Article_Summary{fileNum}.txt"), "w" , encoding="utf-8") as file:
                    file.write(savedSummary)
                    fileNum = fileNum + 1
                print("File Saved. Statistics Updated.")

            else:
                print("Sorry that is not a valid response.")

        repeat = input("Would you like to analyze another article? Please type yes or no and press enter: ")
        if repeat.strip().lower() == "yes":
            articleCount = articleCount + 1
        while repeat.strip().lower() != "yes" and repeat.strip().lower() != "no":
            print("Sorry, that is not a valid response")
            repeat = input("Would you like to analyze another article? Please type yes or no and press enter: ")
        if repeat.strip().lower() == "no": 
            redo = False

#directing users to exit
if repeat.strip().lower() == "no": 
    print("Thank you for your time, you may exit.")
