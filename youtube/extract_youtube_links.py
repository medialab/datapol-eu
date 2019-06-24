# So, the idea is to DFS the | entities to collect inlinks
# We then need to collect the webentity upward
import csv
from traph import Traph
from hyphe_utils import lru_to_url

TRAPH_FOLDER = './sample-traph'
OUPUT = './youtube-inlinks.csv'

YOUTUBE_LRUS = [
    's:http|h:com|h:youtube|',
    's:https|h:com|h:youtube|',
    's:http|h:com|h:youtube|h:www|',
    's:https|h:com|h:youtube|h:www|',
    's:http|h:com|h:googleapis|h:youtube|',
    's:https|h:com|h:googleapis|h:youtube|',
    's:http|h:com|h:googleapis|h:youtube|h:www|',
    's:https|h:com|h:googleapis|h:youtube|h:www|',
    's:http|h:be|h:youtu|',
    's:https|h:be|h:youtu|',
    's:http|h:be|h:youtu|h:www|',
    's:https|h:be|h:youtu|h:www|'
]

traph = Traph(folder=TRAPH_FOLDER, debug=True)

def windup_lru(block):
    node = traph.lru_trie.node(block=block)

    lru = node.stem()
    webentity = node.webentity() if node.has_webentity() else None

    for parent in traph.lru_trie.node_parents_iter(node):
        lru = parent.stem() + lru

        if webentity is None and parent.has_webentity():
            webentity = parent.webentity()

    return lru, webentity

of = open(OUPUT, 'w')
writer = csv.DictWriter(of, fieldnames=[ 'source_url', 'youtube_url', 'webentity'])
writer.writeheader()

for youtube_lru in YOUTUBE_LRUS:
    print('Processing %s' % youtube_lru)

    node = traph.lru_trie.lru_node(youtube_lru)

    if not node or not node.exists:
        continue

    for node, lru in traph.lru_trie.webentity_dfs_iter(node, youtube_lru):
        if not node.is_page() or not node.has_inlinks():
            continue

        inlinks_block = node.inlinks()

        for link_node in traph.link_store.link_nodes_iter(inlinks_block):
            source_lru, webentity = windup_lru(link_node.target())

            writer.writerow({
                'youtube_url': lru_to_url(lru),
                'source_url': lru_to_url(source_lru),
                'webentity': webentity
            })
