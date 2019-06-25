#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Liens WEs -> Channels
# Liens Channels -> WEs
# Liens WEs -> WEs
# Liens Channels -> Channels
# - featured (choice of channels)               <-
# - related (algo youtube similarity)
# - recommanded (algo youtube recommandation)

import csv

import networkx as nx


def add_node(graph, node, *attrs, **kwargs):
    if not graph.has_node(node):
        graph.add_node(node, **kwargs)


def add_edge_weight(graph, node1, node2):
    if not graph.has_node(node1):
        print >> sys.stderr, "WARNING, trying to add link from missing node", node1
        return
    if not graph.has_node(node2):
        print >> sys.stderr, "WARNING, trying to add link to missing node", node2
        return
    if not graph.has_edge(node1, node2):
        graph.add_edge(node1, node2, weight=0)
    graph[node1][node2]['weight'] += 1


if __name__ == "__main__":
    csv_WE = sys.argv[1] if len(sys.argv) > 1 else "Polarisation post élections EU.csv"
    csv_YT = sys.argv[2] if len(sys.argv) > 2 else "full_channels.csv"
    links_WE_YT = sys.argv[3] if len(sys.argv) > 3 else "links_webentities_channels.csv"
    links_YT_WE = sys.argv[4] if len(sys.argv) > 4 else "links_channels_webentities.csv"
    G = nx.DiGraph()
    with open(csv_WE) as f:
        for WE in csv.DictReader(f):
            add_node(G, WE["ID"], label=WE["NAME"], url=WE["HOME PAGE"], portee=WE["Portée (TAGS)"], fondation=WE["fondation (TAGS)"], batch=WE["batch (TAGS)"], edito=WE["edito (TAGS)"], parodique=WE["Parodique (TAGS)"], origine=WE["origine (TAGS)"], digital_nativeness=WE["digital nativeness (TAGS)"], WE_type=WE["type (TAGS)"] sexe=WE["Sexe (TAGS)"], parti=WE["Parti (TAGS)"], liste=WE["Liste (TAGS)"])
    channels = {}
    with open(csv_YT) as f:
        for channel in csv.DictReader(f):
            channels[channel["yt_channel_id"]] = True
            add_node(G, channel["yt_channel_id"], label=channel["nom_de_la_chaine"], url=channel["lien_de_la_chaine"], categorie=channel["category"], pays=channel["pays_chaine"], langue=channel["langue_chaine"], likes=channel["likes_totaux"], abonnes=channel["abonnes"], vues=channel["vues"], videos=channel["videos_publiees"])
    with open(links_WE_YT) as f:
        for l in csv.DictReader(f):
            if l["yt_channel_id"] not in channels:
                continue
            add_edge_weight(G, l["webentity_id"], l["yt_channel_id"])
    with open(links_YT_WE) as f:
        for l in csv.DictReader(f):
            if not l["webentity"]:
                continue
            add_edge_weight(G, l["channel"], l["webentity"])

