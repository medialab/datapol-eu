import csv
import sys
import re
from ural import LRUTrie
from tqdm import tqdm
from itertools import chain

URLS_RE = re.compile(r'\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b')

csv.field_size_limit(sys.maxsize)

CORPUS = './corpus.csv'
CHANNEL = './full_channels.csv'
INPUT = './full_videos.csv'
OUTPUT = './youtube-to-corpus.csv'

TRIE = LRUTrie(strip_trailing_slash=True)

with open(CORPUS) as f:
    reader = csv.DictReader(f)

    for line in reader:
        for prefix in line['PREFIXES AS URL'].split(' '):
            TRIE.set(prefix, line)

with open(INPUT) as f, open(CHANNEL) as f2, open(OUTPUT, 'w') as of:
    reader = csv.DictReader(f)
    reader2 = csv.DictReader(f2)
    writer = csv.DictWriter(of, fieldnames=['channel', 'video', 'url', 'webentity'])
    writer.writeheader()

    for line in tqdm(chain(reader2, reader)):
        description = line.get('description', line.get('summary')).strip()

        if not description:
            continue

        for m in re.finditer(URLS_RE, description):
            match = None
            url = m.group(1).strip()

            if not url:
                continue

            try:
                match = TRIE.match(url)
            except:
                pass

            writer.writerow({
                'channel': line['yt_channel_id'],
                'video': line.get('yt_video_id', ''),
                'url': url,
                'webentity': match['ID'] if match else ''
            })
