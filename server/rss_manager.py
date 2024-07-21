from lxml import etree
import os
from datetime import datetime

from config import RSS_FILE_PATH


def update_rss_feed(title, description, file_url, file_size, duration):
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
    etree.SubElement(new_item, "itunes:duration").text = duration

    tree.write(RSS_FILE_PATH, xml_declaration=True, encoding="UTF-8")


def create_initial_rss_feed():
    root = etree.Element("rss", version="2.0", nsmap={
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "content": "http://purl.org/rss/1.0/modules/content/"
    })
    channel = etree.SubElement(root, "channel")
    etree.SubElement(channel, "title").text = "Your Podcast Title"
    etree.SubElement(channel, "link").text = "https://article2audio.com"
    etree.SubElement(channel, "language").text = "en-us"
    etree.SubElement(channel, "itunes:author").text = "Your Name"
    etree.SubElement(channel, "description").text = "Your podcast description"
    etree.SubElement(channel, "itunes:image", href="https://article2audio.com/podcast-cover.jpg")

    tree = etree.ElementTree(root)
    tree.write(RSS_FILE_PATH, xml_declaration=True, encoding="UTF-8", pretty_print=True)


def get_rss_content():
    if not os.path.exists(RSS_FILE_PATH):
        create_initial_rss_feed()
    with open(RSS_FILE_PATH, 'r') as file:
        return file.read()
