from sc_client import client
from sc_client.models import *
from sc_client.constants import *

from sc_kpm import *
from sc_kpm.utils import *
from langdetect import detect

def abstract_search_of_link_by_nrel(main_idtf, keynodes, nrel):
    links = client.get_links_by_content(main_idtf)
    if len(links[0]) == 0 :
        return None
    node_addr_template = ScTemplate()
    node_addr_template.triple_with_relation(
        sc_types.UNKNOWN,
        sc_types.EDGE_D_COMMON_VAR,
        links[0][0],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes[nrel])
    node_addr = client.template_search(node_addr_template)
    if len(node_addr) < 1:
        return None
    return node_addr[0].get(0)

def get_node_by_main_idtf(main_idtf, keynodes):
    return abstract_search_of_link_by_nrel(main_idtf, keynodes, "nrel_main_idtf")

def get_node_by_idtf(main_idtf, keynodes):
    return abstract_search_of_link_by_nrel(main_idtf, keynodes, "nrel_idtf")

def get_main_idtf_of_addr(node_addr:ScAddr, keynodes:ScKeynodes):
    main_idtf_template = ScTemplate()
    main_idtf_template.triple_with_relation(
        node_addr,
        sc_types.EDGE_D_COMMON_VAR,
        "_link",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        keynodes["nrel_main_idtf"])
    main_rrel = client.template_search(main_idtf_template)

    for item in main_rrel:
        return client.get_link_content(item.get(2))[0].data

def get_node_by_some_idtf(node:str, keynodes) -> ScAddr:
    resolved_node = get_node_by_main_idtf(node, keynodes)
    if resolved_node == None :
        resolved_node = get_node_by_idtf(node, keynodes)
    if resolved_node == None :
        resolved_node = keynodes.get(node)
    if not resolved_node.is_valid() :
        return None
    return resolved_node

def add_main_id_to_node(main_idtf:str, node:ScAddr, keynodes:ScKeynodes):
    lang = detect(main_idtf)
    if (lang != "ru") :
        lang = "en"
    main_idtf_link = create_link(main_idtf,ScLinkContentType.STRING, sc_types.LINK_CONST)
    edge = create_edge(sc_types.EDGE_D_COMMON_CONST,node, main_idtf_link)
    create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, keynodes["nrel_main_idtf"], edge) 
    create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,keynodes["lang_"+ lang], main_idtf_link)

def get_node_by_some_idtf_or_create(node:str, is_relation:bool, keynodes:ScKeynodes) -> ScAddr:
    node_scaddr = get_node_by_some_idtf(node, keynodes)
    if node_scaddr == None:
        if (is_relation) :
            node_scaddr = keynodes.resolve(node, sc_types.NODE_CONST_NOROLE)
        else:
            node_scaddr = keynodes.resolve(node, sc_types.NODE_CONST_CLASS)
        add_main_id_to_node(node,node_scaddr,keynodes)
    return node_scaddr

def get_nrel_relations(src_node, trg_node):
    all_related_template = ScTemplate()
    all_related_template.triple_with_relation(
        src_node,
        sc_types.EDGE_D_COMMON_VAR,
        trg_node,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        sc_types.NODE_VAR_NOROLE)
    return client.template_search(all_related_template)


def abstract_search_of_3iterator(src:ScAddr, trg:ScAddr) -> list[ScTemplateResult]:
    all_is = ScTemplate()
    all_is.triple(
        src,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        trg)
    return client.template_search(all_is)


def string_search_of_3iterator(src:ScAddr, trg:ScAddr, keynodes:ScKeynodes) -> list[str]:
    result = abstract_search_of_3iterator(src, trg)
    set = []
    for item in result:
        idtf =  get_main_idtf_of_addr(item.get(0),keynodes)
        if idtf is not None:
            set.append(idtf)
    return set

def get_some_idtf(node: ScAddr, keynodes:ScKeynodes):
    resolved_node = get_main_idtf_of_addr(node, keynodes)
    if resolved_node == None :
        return get_system_idtf(node)
    else :
        return resolved_node