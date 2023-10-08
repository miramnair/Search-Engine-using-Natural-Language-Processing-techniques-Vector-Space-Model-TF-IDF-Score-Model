# Search-Engine-using-Natural-Language-Processing-techniques-Vector-Space-Model-TF-IDF-Score-Model
Search Engine using Natural Language Processing techniques

1) The documents are preprocessed by:
a)	Converting into lower case.
b)	Removing the stop words and punctuations.
c)	Tokenizing and Stemming :  the words are reduced to its root form.


2)The crawler is scheduled to run once every week using time function. 

The code (crawler.py) is using a while loop to continuously check the current time and determine whether it's time to execute the task. 

•	A variable “last_executed” is initially set to 0, indicating that the task has not been executed yet. 
•	The code then enters a loop where it gets the current time using time() and calculates the difference between the current time and the time of the last execution. 
•	If the difference is greater than or equal to the desired time interval of  604800 seconds (7 days/1week ), then the main function is executed (explained in detail below).
•	The variable “last_executed” is then updated to the current time.
•	If the difference between the current time and the time of the last execution is less than the desired time interval, the code uses time.sleep() to wait for 5 seconds before checking again. 
•	This loop will continue indefinitely until the program is manually interrupted or stopped.

In this case, the tasks executed in main function are web crawling, data processing, and writing the results to a CSV file.

**Web crawling**:

•	The requests library is used to retrieve the robots.txt file for the website. The contents of the robots.txt file are parsed, to check whether the crawler is allowed to access the input url and also get the crawl delay. If the script is allowed to access the url, the script proceeds to crawl the website. 
•	The BeautifulSoup library is used to parse the HTML content of each web page, and extract information about each research paper and processes the data.

**Data Processing**:

•	For each publication, check if at least one author  has a corresponding author link associated with it, indicating that they are part of the Coventry staff. 
•	If no author link is found for a publication, then we ignore it.
•	If an author link is found, a user-defined function (csm_check) loops over each link in the author_links list of the publication and waits for the minimum crawl delay before sending a request to the author's profile page. 
•	The function then uses Beautiful Soup to extract the text associated with the author’s profile page. If the text contains the string "Research Centre for Computational Science and Mathematical Modelling", then the author is considered a CSM member and the code extracts information about the publication title, publication date, authors, and abstract.

The code loops through rest of the pages of the website by incrementing the page_num variable, and waits for the minimum crawl delay specified in the robots.txt file before sending another request.
**CSV File :**
•	Finally, the extracted records are written into a csv file for use. 

3) Indexer : The code is provided  with the filename : app.py. It was implemented using inverted index.

•	The function first initializes an empty dictionary called inverted_index. 
•	Next, it loops through each stemmed document, tokenizes the document by splitting it into individual words, and counts the frequency of each word (i.e., the term frequency). The term frequency is stored in a dictionary called term_freq, with the word as the key and the frequency as the value.
•	For each word in the document, the function then updates the inverted_index dictionary with the term frequency and document index information. If the word is already a key in the inverted_index dictionary, the function adds the document index and term frequency to the existing entry. Otherwise, it creates a new entry for the word and adds the document index and term frequency.

Format of inverted_index : {‘keyword’: {document_index, term_frequency}}

4) Query Processor: The code is provided  with the filename : app.py

The queries are preprocessed by:
1)	Converting it into lower case.
2)	Removing the stop words and punctuations.
3)	Tokenizing and Stemming :  the words are reduced to its root form.

**Query processing steps** :

•	The function first initializes an empty set called qdocs to store the document ids that contain any of the query terms. 
•	Then, the code tokenizes the query and applies stemming to the query terms using a function called stemmer_query (user-defined in code).
•	The function then iterates through the stemmed query terms, checking if each term is in the inverted index (a dictionary where the keys are terms and the values are another dictionary containing the document ids and their corresponding term frequencies). If the term is in the inverted index, the function updates ‘qdocs’ with the set of document ids that contain the term.
•	The code also calculates the document frequency for each query term (i.e., the number of documents in the inverted index that contain the term). 
•	For each term in the query that is found in the inverted index, the function calculates the tf-idf score for each document that contains the term. This is done by multiplying the term frequency for the term in the document by the idf (inverse document frequency) score for the term, where idf is defined as N/df (where N is the total number of documents in the inverted index). 
•	Finally, the function sorts the document ids by their tf-idf scores in descending order (highest score first) and returns the sorted list of document ids.
