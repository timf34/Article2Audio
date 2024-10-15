# rss_manager.py
import os
from lxml import etree
from datetime import datetime
import random

def get_rss_file_path(user_id):
    rss_dir = os.path.join('rss_feeds')
    if not os.path.exists(rss_dir):
        os.makedirs(rss_dir)
    return os.path.join(rss_dir, f'rss_{user_id}.xml')

def update_rss_feed(
        title: str,
        author_name: str,
        description: str,
        file_url: str,
        file_size: str,
        duration: str,
        user_id: str
) -> None:

    rss_file_path = get_rss_file_path(user_id)
    if not os.path.exists(rss_file_path):
        print("RSS file not found... Creating new initial RSS feed")
        create_initial_rss_feed(user_id)

    try:
        tree = etree.parse(rss_file_path)
        root = tree.getroot()
        channel = root.find("channel")

        new_item = etree.SubElement(channel, "item")
        etree.SubElement(new_item, "title").text = title
        etree.SubElement(new_item, "description").text = description
        etree.SubElement(new_item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        # Generating a unique identifier for the item using a timestamp and a random number
        guid_text = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}-{random.randint(1000, 9999)}"
        etree.SubElement(new_item, "guid", isPermaLink="false").text = guid_text

        etree.SubElement(new_item, "enclosure", url=file_url, length=file_size, type="audio/mpeg")

        etree.SubElement(new_item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = duration
        etree.SubElement(new_item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit").text = "false"
        etree.SubElement(new_item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = author_name

        etree.indent(tree, space="\t", level=0)
        tree.write(rss_file_path, xml_declaration=True, encoding="UTF-8", pretty_print=True)

        print(f"RSS feed successfully updated with title: {title}")

    except Exception as e:
        print(f"Error updating RSS feed: {e}")


def create_initial_rss_feed(user_id):
    rss_file_path = get_rss_file_path(user_id)
    # Optionally, retrieve user info from the database
    # For simplicity, we can just use placeholders
    # TODO: fix this going forward!
    user_name = "User's Articles"
    user_email = "user@example.com"

    nsmap = {
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'atom': 'http://www.w3.org/2005/Atom'
    }
    root = etree.Element("rss", version="2.0", nsmap=nsmap)
    channel = etree.SubElement(root, "channel")
    etree.SubElement(channel, "title").text = f"{user_name}"
    etree.SubElement(channel, "link").text = "https://article2audio.com"
    etree.SubElement(channel, "language").text = "en-us"
    etree.SubElement(channel, "copyright").text = "© 2024 Article2Audio"
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = user_name
    etree.SubElement(channel, "description").text = f"{user_name}'s articles"
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image", href="https://article2audio.com/podcast_cover.jpg")
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category", text="Technology")
    etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit").text = "false"
    etree.SubElement(channel, "{http://www.w3.org/2005/Atom}link", href=f"https://article2audio.com/rss/{user_id}.xml", rel="self", type="application/rss+xml")

    owner = etree.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}owner")
    etree.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}name").text = user_name
    etree.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}email").text = user_email

    tree = etree.ElementTree(root)
    tree.write(rss_file_path, xml_declaration=True, encoding="UTF-8", pretty_print=True)

def get_rss_content(user_id):
    rss_file_path = get_rss_file_path(user_id)
    if not os.path.exists(rss_file_path):
        create_initial_rss_feed(user_id)
    with open(rss_file_path, 'r') as file:
        return file.read()
