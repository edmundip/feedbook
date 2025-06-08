#!/usr/bin/env python3

import os
import sys
sys.path.append('./.python.lib')
from datetime import datetime
import feedparser
import zipfile

def save_content(feed, title, content_template_filename, content_output_filename):
    # read the content template file
    with open(content_template_filename, 'r') as content_template_file:
        content_content = content_template_file.read()
    content_template_file.close()

    # update the content content
    content_content = content_content.replace('{{title}}', title)

    manifest_article = ''
    for index, entry in enumerate(feed.entries, start=1):
        manifest_article = manifest_article + \
            f'\n        <item id="article{index}" href="article{index}.xhtml" media-type="application/xhtml+xml"/>'
    content_content = content_content.replace('{{manifest_article}}', manifest_article)

    toc_article = ''
    for index, entry in enumerate(feed.entries, start=1):
        toc_article = toc_article + f'\n        <itemref idref="article{index}"/>'
    content_content = content_content.replace('{{toc_article}}', toc_article)


    # write the content content
    with open(content_output_filename, 'w') as content_output_file:
        content_output_file.write(content_content)
    content_output_file.close()

def save_toc(feed, title, toc_template_filename, toc_output_filename):
    # read the toc template file
    with open(toc_template_filename, 'r') as toc_template_file:
        toc_content = toc_template_file.read()
    toc_template_file.close()

    # update the toc content
    toc_content = toc_content.replace('{{title}}', title)

    nav_point = ''
    for index, entry in enumerate(feed.entries, start=1):
        nav_point = nav_point + \
f'''        <navPoint id="navPoint-{index}" playOrder="{index}">
            <navLabel>
                <text>{entry.title}</text>
            </navLabel>
            <content src="article{index}.xhtml"/>
        </navPoint>
'''
    toc_content = toc_content.replace('{{nav_point}}', nav_point)

    # write the toc content
    with open(toc_output_filename, 'w') as toc_output_file:
        toc_output_file.write(toc_content)
    toc_output_file.close()

def save_cover(feed, title, cover_template_filename, cover_output_filename):
    # read the cover template file
    with open(cover_template_filename, 'r') as cover_template_file:
        cover_content = cover_template_file.read()
    cover_template_file.close()

    # update the cover content
    published = datetime.now().strftime("%a, %d %b %Y %H:%M")
    cover_content = cover_content.replace('{{title}}', title)
    cover_content = cover_content.replace('{{published}}', published)

    # write the cover content
    with open(cover_output_filename, 'w') as cover_output_file:
        cover_output_file.write(cover_content)
    cover_output_file.close()

def save_article(entry, article_template_filename, article_output_filename):
    # read the article template file
    with open(article_template_filename, 'r') as article_template_file:
        article_content = article_template_file.read()
    article_template_file.close()

    # update the article content
    article_content = article_content.replace('{{title}}', entry.title)
    article_content = article_content.replace('{{summary}}', entry.summary)

    # write the article content
    with open(article_output_filename, 'w') as article_output_file:
        article_output_file.write(article_content)
    article_output_file.close()

def create_book(book_content_folderpath, book_output_filename="output.epub"):
    # add 'mimetype' file with no compression
    with zipfile.ZipFile(book_output_filename, 'w') as zipf:
        mimetype_path = os.path.join(book_content_folderpath, 'mimetype')
        zipf.write(mimetype_path, arcname='mimetype', compress_type=zipfile.ZIP_STORED)

        # add META-INF and OEBPS folders with maximum compression
        for folder in ['META-INF', 'OEBPS']:
            folder_path = os.path.join(book_content_folderpath, folder)
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, book_content_folderpath)  # Adjust path for ZIP
                    zipf.write(filepath, arcname=arcname, compress_type=zipfile.ZIP_DEFLATED)
    zipf.close()

def cleanup_folder(book_content_folderpath):
    oebps_folder = os.path.join(book_content_folderpath, 'OEBPS')
    for filename in os.listdir(oebps_folder):
        if filename.startswith('article'):
            file_path = os.path.join(oebps_folder, filename)
            os.remove(file_path)

def make_feedbook(rss_feed_url, title, output_file_epub):
    feed = feedparser.parse(rss_feed_url)

    cleanup_folder('./book')
    save_content(feed, title, './book/template/content.opf', './book/OEBPS/content.opf')
    save_toc(feed, title, './book/template/toc.ncx', './book/OEBPS/toc.ncx')
    save_cover(feed, title, './book/template/cover.xhtml', './book/OEBPS/cover.xhtml')
    for index, entry in enumerate(feed.entries, start=1):
        save_article(entry, './book/template/article.xhtml', f"./book/OEBPS/article{index}.xhtml")
    create_book('./book', output_file_epub)

def main():
    if len(sys.argv) == 4:
        make_feedbook(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print('./feedbook.py [rss_feed_url] [title] [output_file_epub]')

if __name__ == "__main__":
    main()
