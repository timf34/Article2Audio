from lxml import etree
import os
from datetime import datetime

from config import RSS_FILE_PATH


def update_rss_feed(title, description, file_url, file_size, duration) -> None:
    if not os.path.exists(RSS_FILE_PATH):
        create_initial_rss_feed()

    tree = etree.parse(RSS_FILE_PATH)
    root = tree.getroot()
    channel = root.find("channel")

    new_item = etree.SubElement(channel, "item")
    etree.SubElement(new_item, "title").text = title
    etree.SubElement(new_item, "description").text = description
    etree.SubElement(new_item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    etree.SubElement(new_item, "guid", isPermaLink="false").text = file_url
    enclosure = etree.SubElement(new_item, "enclosure", url=file_url, length=str(file_size), type="audio/mpeg")
    etree.SubElement(new_item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = duration
    etree.SubElement(new_item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit").text = "false"
    etree.SubElement(new_item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = "Tim"

    etree.indent(tree, space="\t", level=0)
    tree.write(RSS_FILE_PATH, xml_declaration=True, encoding="UTF-8", pretty_print=True)


def create_initial_rss_feed():
    nsmap = {
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'atom': 'http://www.w3.org/2005/Atom'
    }
    root = etree.Element("rss", version="2.0", nsmap=nsmap)
    channel = etree.SubElement(root, "channel")
    etree.SubElement(channel, "title").text = "Tim's Articles"
    etree.SubElement(channel, "link").text = "https://article2audio.com"
    etree.SubElement(channel, "language").text = "en-us"
    etree.SubElement(channel, "copyright").text = "© 2024 Tim Farrelly"
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = "Tim Farrelly"
    etree.SubElement(channel, "description").text = "Tim's articles"
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image", href="https://article2audio.com/podcast_cover.jpg")
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category", text="Technology")
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit").text = "false"
    etree.SubElement(channel, "{http://www.w3.org/2005/Atom}link", href="https://article2audio.com/rss.xml", rel="self", type="application/rss+xml")

    owner = etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}owner")
    etree.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}name").text = "Tim Farrelly"
    etree.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}email").text = "timf34@gmail.com"

    tree = etree.ElementTree(root)
    tree.write(RSS_FILE_PATH, xml_declaration=True, encoding="UTF-8", pretty_print=True)


def get_rss_content():
    if not os.path.exists(RSS_FILE_PATH):
        create_initial_rss_feed()
        get_rss_content()
    with open(RSS_FILE_PATH, 'r') as file:
        return file.read()
