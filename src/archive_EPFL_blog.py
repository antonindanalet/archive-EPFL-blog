from urllib.request import urlopen, urlretrieve
from urllib.parse import unquote
import urllib.error
from bs4 import BeautifulSoup
import os
from pathlib import Path

name_of_the_blog = 'tavie'  # Make the name of the blog a global variable

# Create the directory for the archive
directory_path = Path('../archives/' + name_of_the_blog)


def archives_blog():
    if not directory_path.exists():
        os.mkdir(directory_path)
    print('Reading the landing page...')
    url = 'http://blogs.epfl.ch/' + name_of_the_blog
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    print('Saving articles of the landing page...')
    archive_articles_of_a_page(soup)
    print('Saving pages of the blog...')
    archive_pages_of_the_blog(soup)
    print('Saving categories of the blog...')
    archive_categories_of_the_blog(soup)
    print('Archiving the landing page as index.html...')
    archive_landing_page(soup)


def archive_articles_of_a_page(soup, level=1, download=True):
    # Create the directory for the articles
    if download is True:
        article_path = directory_path / 'article'
        if not article_path.exists():
            os.mkdir(article_path)
    # Archive article of a page (and replace internet links by local links for "posted by" links)
    for tag_article in soup.find_all('div', {'class': 'article-posted-by'}):
        a_article = tag_article.find('a', href=True)
        url_article = a_article['href']
        number_article = a_article['href'].split('/')[-1]
        # Replace internet links by local links in the page
        if level == 1:
            a_article['href'] = 'article/' + number_article + '.html'  # "Posted by" link
        elif level == 2:
            a_article['href'] = '../article/' + number_article + '.html'  # "Posted by" link
        elif level == 3:
            a_article['href'] = '../../article/' + number_article + '.html'  # "Posted by" link
        if download is True:
            # Save the content of the article
            html_article = urlopen(url_article)
            soup_article = BeautifulSoup(html_article, 'lxml')
            change_links_and_use_internal_ones(soup_article, level=2)
            with open(Path('../archives/' + name_of_the_blog + '/article/' + number_article + '.html'), 'w') as file:
                file.write(str(soup_article))


def change_links_and_use_internal_ones(soup, level):
    # Change the link to the EPFL logo
    soup = save_logo(soup, download=False, level=level)
    # Change the link to the pictures
    soup = save_pictures_of_the_blog(soup, download=False, level=level)
    # Change the links to CSS
    save_css(soup, download=False, level=level)
    # Change the link to "home"
    archive_documents_of_a_page_and_change_links_to_home(soup, level=level, download=False)
    # Change the links to the categories
    change_links_to_categories(soup, level=level)


def archive_pages_of_the_blog(soup):
    # Create the directory for the pages
    pages_path = directory_path / 'pages'
    if not pages_path.exists():
        os.mkdir(pages_path)
    # Initialize the loop
    soup_next = soup
    next_pages_exists = True
    page_number = 1
    # Get the next page (from landing page to page 2)
    tag_next = soup_next.find('a', {'id': 'linkNextPage'})
    if tag_next is None:  # Test if there is a second page
        next_pages_exists = False
    else:
        url_of_the_next_page = tag_next['href']
    while next_pages_exists:
        if tag_next is None:  # Test if there is a page n+1 when there is a least a page 2
            next_pages_exists = False
        else:
            page_number += 1
            print('Saving page ' + str(page_number) + '...')
            url_of_the_next_page = 'http://blogs.epfl.ch' + url_of_the_next_page
            html_next = urlopen(url_of_the_next_page)
            soup_next = BeautifulSoup(html_next, 'lxml')
            change_links_and_use_internal_ones(soup_next, level=2)
            # Replace links to comments of the article
            soup_next = replace_links_to_comments(soup_next, level=2)
            # Get the next page (from page n to page n+1)
            tag_next = soup_next.find('a', {'id': 'linkNextPage'})
            try:
                url_of_the_next_page = tag_next['href']
            except TypeError:
                pass
            # Change the page links at the bottom of the page
            soup_next = change_page_links(soup_next, level=2)
            # Save all articles of this page
            archive_articles_of_a_page(soup_next, level=2)
            # Save the page
            with open(Path('../archives/' + name_of_the_blog + '/pages/' + str(page_number) + '.html'), 'w') as file:
                file.write(str(soup_next))


def archive_categories_of_the_blog(soup):
    # Create the directory for the pages
    categories_path = directory_path / 'category'
    if not categories_path.exists():
        os.mkdir(categories_path)
    tag_category_list = soup.find('ul', {'class': 'tree'}).find_all('li', {'class': 'inpath'})[1]
    for tag_category in tag_category_list.find_all('a'):
        # Create folder for the category
        number_of_category = tag_category['href'].split('/')[-1]
        category_path = directory_path / 'category' / number_of_category
        if not category_path.exists():
            os.mkdir(category_path)
        # Save the landing page of the category
        html_category = urlopen('https://blogs.epfl.ch/' + str(tag_category['href']))
        soup_category = BeautifulSoup(html_category, 'lxml')
        change_links_and_use_internal_ones(soup_category, level=3)
        # Replace links to articles
        archive_articles_of_a_page(soup_category, level=3, download=False)
        # Replace links to comments of the article
        soup_category = replace_links_to_comments(soup_category, level=3)
        # Save other pages of the category
        archive_page_of_categories_of_the_blog(soup_category, number_of_category)
        # Look if there is a "next page"
        tag_next = soup_category.find('a', {'id': 'linkNextPage'})
        if tag_next is not None:  # If there is a second page, change links to other pages of the category
            soup_category = change_page_links(soup_category, number_of_category=number_of_category)
        # Save the landing page of the category
        path_to_categories = Path('../archives/' + name_of_the_blog + '/category/' + number_of_category)
        with open(path_to_categories / 'index.html', 'w') as file:
            file.write(str(soup_category))
        # Change links for the category
        #tag_category['href'] = Path('category/' + number_of_category + '/index.html')
    return soup


def archive_landing_page(soup):
    soup = save_logo(soup)  # Locally save the EPFL logo
    soup = save_pictures_of_the_blog(soup)
    soup = save_css(soup)  # Locally save the 2 CSS files
    # Replace page links
    soup = change_page_links(soup)
    # Replace internet links by local links for "comments" link (link to an article, but the "comments" part)
    soup = change_links_to_categories(soup, level=1)
    # Replace "home" link by local link (and all links to landing page) and downloads documents hosted on the blog
    archive_documents_of_a_page_and_change_links_to_home(soup)
    # Save other elements
    replace_links_to_comments(soup)
    # Save the landing page, index.html
    with open(Path('../archives/' + name_of_the_blog + '/index.html'), 'w') as file:
        file.write(str(soup))


def archive_page_of_categories_of_the_blog(soup_category, number_of_category):
    # Initialize the loop
    #global url_next
    soup_next = soup_category
    next_pages_exists = True
    page_number = 1
    # Get the next page (from landing page of the category to page 2 of the category)
    tag_next = soup_next.find('a', {'id': 'linkNextPage'})
    if tag_next is None:  # Test if there is a second page
        next_pages_exists = False
    else:
        url_next = tag_next['href']
    while next_pages_exists:
        if tag_next is None:  # Test if there is a page n+1 when there is a least a page 2
            next_pages_exists = False
        else:
            page_number += 1
            url_next = 'http://blogs.epfl.ch' + url_next
            html_next = urlopen(url_next)
            soup_next = BeautifulSoup(html_next, 'lxml')
            change_links_and_use_internal_ones(soup_next, level=3)
            # Replace lint to articles
            archive_articles_of_a_page(soup_next, level=3, download=False)
            # Replace links to comments of the article
            soup_next = replace_links_to_comments(soup_next, level=3)
            # Get the next page (from page n to page n+1)
            tag_next = soup_next.find('a', {'id': 'linkNextPage'})
            try:
                url_next = tag_next['href']
            except TypeError:
                pass
            # Change the page links at the bottom of the page
            soup_next = change_page_links(soup_next, number_of_category=number_of_category)
            # Save the page
            with open(Path('../archives/' + name_of_the_blog + '/category/' + str(number_of_category) + '/' +
                           str(page_number) + '.html'), 'w') as file:
                file.write(str(soup_next))


def archive_documents_of_a_page_and_change_links_to_home(soup, level=1, download=True):
    # Replace internal links of the blog by local links and download the documents hosted by the blog
    for tag_link in soup.find_all('a', href=True):
        # Replace links to landing page, aka 'home',
        if tag_link['href'] == 'https://blogs.epfl.ch/' + name_of_the_blog:
            if level == 1:
                tag_link['href'] = 'index.html'
            elif level == 2:
                tag_link['href'] = '../index.html'
            elif level == 3:
                tag_link['href'] = '../../index.html'
        # Replace links to documents hosted by the blog and archive them
        elif str(tag_link['href']).startswith('https://blogs.epfl.ch/' + name_of_the_blog + '/documents/'):
            url_link = tag_link['href']
            subpath_of_the_file = url_link.split('https://blogs.epfl.ch/' + name_of_the_blog + '/documents/')[1]
            name_of_the_file = subpath_of_the_file.split('/')[-1]
            subfolder_of_the_file = subpath_of_the_file.split(name_of_the_file)[0]
            # Download the file
            if download is True:
                documents_path = directory_path / 'documents'
                subfolder_complete_path = documents_path / subfolder_of_the_file
                if not subfolder_complete_path.exists():
                    subfolder_complete_path.mkdir(parents=True)
                urlretrieve(url_link, documents_path / subfolder_of_the_file / unquote(name_of_the_file))
            # Replace the path of the file by a local path
            tag_link['href'] = Path('documents/') / subfolder_of_the_file / name_of_the_file


def change_links_to_categories(soup, level):
    tag_category_list = soup.find('ul', {'class': 'tree'}).find_all('li', {'class': 'inpath'})[1]
    for tag_category in tag_category_list.find_all('a'):
        # Extract the number of the category
        number_of_category = tag_category['href'].split('/')[-1]
        # Change links for the category
        if level == 1:
            tag_category['href'] = Path('category/' + number_of_category + '/index.html')
        elif level == 2:
            tag_category['href'] = Path('../category/' + number_of_category + '/index.html')
        elif level == 3:
            tag_category['href'] = Path('../../category/' + number_of_category + '/index.html')
    return soup


def change_page_links(soup, level=1, number_of_category=None):
    if number_of_category is None:
        for tag_page in soup.find('tfoot').find_all('a'):
            if tag_page['href'] == '/' + name_of_the_blog:
                tag_page['href'] = '../index.html'
            else:
                nb_page = tag_page['href'].split('=')[1]
                if level == 1:
                    tag_page['href'] = 'pages/' + nb_page + '.html'
                elif level == 2:
                    tag_page['href'] = '../pages/' + nb_page + '.html'
    else:
        for tag_page in soup.find('tfoot').find_all('a'):
            if tag_page['href'] == '/category/' + number_of_category:
                tag_page['href'] = '../' + number_of_category + '/index.html'
            else:
                nb_page = tag_page['href'].split('=')[1]
                tag_page['href'] = nb_page + '.html'
    return soup


def replace_links_to_comments(soup, level=1):
    for tag_article_comments in soup.find_all('div', {'class': 'article-posted-comments'}):
        a_article_comments = tag_article_comments.find('a', href=True)
        number_article = a_article_comments['href'].split('#')[0].split('/')[-1]
        if level == 1:
            a_article_comments['href'] = 'article/' + number_article + '.html#comments'
        elif level == 2:
            a_article_comments['href'] = '../article/' + number_article + '.html#comments'
        elif level == 3:
            a_article_comments['href'] = '../../article/' + number_article + '.html#comments'
    return soup


def save_pictures_of_the_blog(soup, download=True, level=1):
    if download is True:
        documents_path = directory_path / 'documents'
        if not documents_path.exists():
            os.mkdir(documents_path)
        external_images_path = directory_path / 'external_images'
        if not external_images_path.exists():
            os.mkdir(external_images_path)
    for tag_image in soup.find_all('img'):
        if tag_image.has_attr('src'):
            src_image = str(tag_image['src'])
            name_of_the_image = src_image.split('/')[-1]
            if src_image.startswith('https://blogs.epfl.ch/' + name_of_the_blog + '/documents/'):
                if download is True:
                    urlretrieve(src_image, documents_path / unquote(name_of_the_image))
                # Replace the path of the image by a local path
                if level == 1:
                    tag_image['src'] = Path('documents/') / name_of_the_image  # Path for index.html
                elif level == 2:
                    tag_image['src'] = Path('../documents/') / name_of_the_image  # Path for articles in folder "article"
                elif level == 3:
                    tag_image['src'] = Path('../../documents/') / name_of_the_image  # Path for articles in folder "article"
            elif src_image.startswith('http'):
                if download is True:
                    try:
                        urlretrieve(src_image, external_images_path / unquote(name_of_the_image))
                    except urllib.error.HTTPError as e:
                        with open(directory_path / 'warning.txt', 'a') as file:
                            file.write(src_image + ' ' + str(e) + '\n')
                    except urllib.error.URLError as e:
                        with open(directory_path / 'warning.txt', 'a') as file:
                            file.write(src_image + ' ' + str(e) + '\n')
                    # Replace the path of the image by a local path
                    tag_image['src'] = Path('external_images/') / name_of_the_image  # Path for index.html
                else:
                    # Replace the path of the image by a local path, path for articles in folder "article"
                    tag_image['src'] = Path('../external_images/') / name_of_the_image
    return soup


def save_logo(soup, download=True, level=1):
    tag_logo = soup.find('div', {'id': 'header2013'}).find('div', {'id': 'nav-logo'}).find('img')
    if download is True:
        image_path = directory_path / 'epfl_stuff'
        if not image_path.exists():
            os.mkdir(image_path)
        url_logo = tag_logo['src']
        # Remove the // at the beginning of the path and add https://
        url_logo = 'https://' + url_logo[2:]
        urlretrieve(url_logo, image_path / 'epfl_logo.png')
    # Replace the path of the logo by a local path
    if level == 1:
        tag_logo['src'] = Path('epfl_stuff/') / 'epfl_logo.png'
    elif level == 2:
        tag_logo['src'] = Path('../epfl_stuff/') / 'epfl_logo.png'
    elif level == 3:
        tag_logo['src'] = Path('../../epfl_stuff/') / 'epfl_logo.png'
    return soup


def save_css(soup, download=True, level=1):
    for tag_css in soup.find_all('link', {'rel': 'stylesheet'}):
        css_name = tag_css['href'].split('/')[-1]
        if download is True:
            css_path = directory_path / 'epfl_stuff'
            if not css_path.exists():
                os.mkdir(css_path)
            url_csv = tag_css['href']
            urlretrieve(url_csv, css_path / css_name)
        # Replace the path of the logo by a local path
        if level == 1:
            tag_css['href'] = Path('epfl_stuff/') / css_name
        elif level == 2:
            tag_css['href'] = Path('../epfl_stuff/') / css_name
        elif level == 3:
            tag_css['href'] = Path('../../epfl_stuff/') / css_name
    return soup


if __name__ == '__main__':
    archives_blog()
