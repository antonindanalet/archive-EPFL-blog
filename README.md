# Archiving blogs hosted on epfl.ch (blogs.epfl.ch)
This code generates a local archive of an EPFL blog. This archive contains the landing page, the different pages of the blog, the articles, the comments, the pictures posted on the blog and the documents hosted on the blog.

## Getting started
These instructions will get you a copy of the project up and running on your local machine for archiving a blog.

### Prerequisites
To run the code itself, you need python 3 and beautifulsoup4 (bs4).

### Run the code
Just enter the name of the blog you want to archive in line 8 (currently "tavie") and run the code.

## Known issues
When archiving tavie, after around 77 pages and 780 articles saved, opening the page containing an article (`html_article = urlopen(url_article)`) is not possible anymore and the following error happens: `urllib.error.URLError: <urlopen error [Errno 61] Connection refused>`
