from urllib.robotparser import RobotFileParser
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
import csv
import os
import datetime
import pandas as pd


class WebsiteCrawler:
    def __init__(self, url):
        self.url = url

    def csm_check(self,author_links,linked_authors,csm,crawl_delay):
        """ This function crawls the profile page and check if they are part of CSM"""
        csm_member = "FALSE"
        for i, link in enumerate(author_links):
            if crawl_delay:
                time.sleep(crawl_delay)
            try:
                response_link = requests.get(link)
            except requests.exceptions.RequestException as exception:
                print("An error occurred:", exception)
            soup_link = BeautifulSoup(response_link.content, "html.parser")
            soup_text = soup_link.find("a", class_='link primary')
            if soup_text != None:
                soup_text = soup_text.string
                if "Research Centre for Computational Science and Mathematical Modelling" in soup_text:
                    csm_member = "TRUE"
                    csm.append(linked_authors[i])
        return(csm_member,csm)

    def crawl(self):
        """This function crawls through each publication and stores data if any author is part of CSM"""
        parsed_url = urllib.parse.urlparse(url)
        # Send a request to retrieve the robots.txt file
        root_url = parsed_url.scheme + '://' + parsed_url.netloc
        # Append '/robots.txt' to the root URL
        robot_url = root_url + '/robots.txt'
        response = requests.get(robot_url)
        # Parse the contents of the robots.txt file
        rp = RobotFileParser()
        rp.parse(response.text.splitlines())
        # Check if the crawler is allowed to access the URL
        if rp.can_fetch('*', url):
            # Get the minimum crawl delay (in seconds) specified in the robots.txt file
            crawl_delay = rp.crawl_delay('*')
            if crawl_delay:
                # Calculate the hit rate based on the crawl delay
                hit_rate = 1 / crawl_delay
                print(f'The minimum time between requests is {crawl_delay:.2f} seconds')
                print(f'The maximum hit rate is {hit_rate:.2f} requests per second')

            # Crawl the research papers website
            papers = []
            csm = []
            for page_num in range(0, 6):
                # Wait for the minimum crawl delay before sending another request
                if crawl_delay:
                    time.sleep(crawl_delay)
                page_url = f'{url}?page={page_num}'
                try:
                    response = requests.get(page_url)
                except requests.exceptions.RequestException as exception:
                    print("An error occurred:", exception)
                soup = BeautifulSoup(response.content, "html.parser")
                results = soup.find_all(class_="result-container")
                for i, result in enumerate(results):
                    paper = {}
                    if result.find(class_="link person"):
                        authors = result.find_all(class_="link person")
                        author_names = [author.get_text().strip() for author in authors if author.has_attr('href')]
                        author_links = [author.get('href') for author in authors if author.has_attr('href')]
                        csm_member,csm = self.csm_check(author_links,author_names,csm,crawl_delay)
                        if(csm_member == "TRUE"):
                            title = result.find(class_="title")
                            if title is not None:
                                title_link = title.find(class_="link")
                                paper["title"] = title.get_text().strip()
                                paper["title_link"] = title_link.get('href')
                            date = result.find(class_="date")
                            if date is not None:
                                paper["date"] = date.get_text().strip()
                            span1 = []
                            for span in result.select('h3.title ~ span:not([class])'):
                                if span.find_previous_sibling() is None or not span.find_previous_sibling().has_attr('rel='):
                                    span1.append(span.text.strip())
                            author_names_nolink = []
                            for value in span1:
                                author_names_nolink.append(value)
                            paper["non_cov_authors"] = author_names_nolink
                            paper["non_cov_authors"] = author_names_nolink
                            for a in author_names:
                                paper["cov_authors"] = author_names
                            paper["author_links"] = author_links
                            abstract_repsonse = requests.get(paper["title_link"])
                            soup_abstract_response = BeautifulSoup(abstract_repsonse.content, "html.parser")
                            abstract_results = soup_abstract_response.find('div', {'class': 'textblock'})
                            if abstract_results != None:
                                paragraph = abstract_results.text
                                paper["abstract"] = paragraph
                            else:
                                paper["abstract"] = "No abstract info..."
                            papers.append(paper)

        return papers,csm



# Main function call
url = "https://pureportal.coventry.ac.uk/en/organisations/research-centre-for-computational-science-and-mathematical-modell/publications/"
webcrawl = WebsiteCrawler(url)


#Schedule the execution to run once a week
last_executed = 0  # initialize the time of the last execution
while True:
    current_time = time.time()  # get the current time
    print("current_time",current_time)
    # Execute every week
    #if current_time - last_executed >= 604800:
    # Execute every 3minutes for testing purposes
    if current_time - last_executed >= 180:
        papers,csm = webcrawl.crawl()
        # Use a dictionary to count the frequency of each author
        freq_dict = {}
        for elem in csm:
            if elem in freq_dict:
                freq_dict[elem] += 1
            else:
                freq_dict[elem] = 1
        # Convert the dictionary to a Pandas dataframe
        df = pd.DataFrame(list(freq_dict.items()), columns=['Author', 'Publication#'])
        # Display the dataframe
        print(df.to_string(index=False))
        print("Number of CSM Staff :",len(df))
        filename = "result_papers.csv"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, filename)
        with open(csv_path, mode="w", newline="") as csvfile:
            execution_time = datetime.datetime.now()
            print("The files were updated on",execution_time.strftime("%Y-%m-%d %H:%M:%S"))
            columns = ["title", "title_link", "date", "cov_authors", "author_links","non_cov_authors", "abstract"]
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for paper in papers:
                writer.writerow(paper)
        last_executed = current_time
    #check again after 5 secs, if it's not execution time yet
    time.sleep(5)
