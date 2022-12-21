from sc_client import client
from sc_client.models import *
from sc_client.constants import *

from sc_kpm import *
from sc_kpm.utils import *
from .models import entity, relation, Set
from .search import string_search_of_3iterator, abstract_search_of_3iterator, add_main_id_to_node
from .search import get_some_idtf, get_nrel_relations, get_main_idtf_of_addr
from .search import get_node_by_some_idtf_or_create, get_node_by_some_idtf 

def get_all_child_sets(node_addr, keynodes):
    return string_search_of_3iterator(node_addr, "_trg", keynodes)

def get_all_parent_sets(node_addr, keynodes):
    return string_search_of_3iterator("_src", node_addr, keynodes)

def get_all_sets(node_addr, keynodes) :
    return Set(
        parent= get_all_parent_sets(node_addr, keynodes),
        child=get_all_child_sets(node_addr, keynodes)
    )

def get_all_nrel_relations(node_addr, keynodes):
    all_related = get_nrel_relations(src_node= node_addr, trg_node= sc_types.NODE_VAR)
    all_related.extend(get_nrel_relations(src_node= sc_types.NODE_VAR, trg_node= node_addr))
    relations = []
    for item in all_related:
        src_addr = item.get(0)
        trg_addr = item.get(2)
        rrel_arg = item.get(3)
        src = get_main_idtf_of_addr(src_addr, keynodes)
        trg = get_main_idtf_of_addr(trg_addr, keynodes)
        rrel = get_some_idtf(rrel_arg, keynodes)
        if (src is None):
            src = get_all_child_sets(src_addr, keynodes)
        if (trg is None):
            trg = get_all_child_sets(trg_addr, keynodes)
        relations.append(
            relation(src, 
                     trg, 
                     rrel))
    return relations 

def get_entity_by_idtf(node:str, keynodes:ScKeynodes) :
    node_addr = get_node_by_some_idtf(node, keynodes)
    if node_addr == None :
        return None
    all_rrels = get_all_nrel_relations(node_addr, keynodes)
    concept_belongs = get_all_sets(node_addr, keynodes)
    return entity (
        main_idtf=get_some_idtf(node_addr, keynodes),
        system_idtf=get_system_idtf(node_addr),
        relations=all_rrels,
        sets=concept_belongs
    )

def relation_to_system_view(rel_name:str):
    rel_name = rel_name.strip()
    if rel_name.find("*") == -1:
        rel_name = rel_name + "*"
    return " " + rel_name + " "

def create_node_with_multiple_nodes(nodes:list, keynodes:ScKeynodes) :
    empty_node = create_node(sc_types.NODE_CONST)
    for node in nodes:
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,empty_node, get_node_by_some_idtf_or_create(node, False, keynodes))
    return empty_node

def get_relation_node_from_idtf_or_list(node, keynodes:ScKeynodes):
    if isinstance(node, list) :
        return create_node_with_multiple_nodes(node, keynodes)
    else:
        return get_node_by_some_idtf_or_create(node, False, keynodes)

def add_relations_to_node(relations:list, keynodes:ScKeynodes):
    for relation in  relations:
        src_name = relation.src
        trg_name = relation.trg
        sys_relation_name = relation_to_system_view(relation.name)
        relation = get_node_by_some_idtf_or_create(sys_relation_name, True, keynodes)
        src = get_relation_node_from_idtf_or_list(src_name, keynodes)
        trg = get_relation_node_from_idtf_or_list(trg_name, keynodes)
        edge = create_edge(sc_types.EDGE_D_COMMON_CONST,src, trg)
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM, relation, edge)

def fill_search_template(search_template:ScTemplate, triple_source:str, triple_target:ScAddr, five_source:str, five_target:ScAddr):
    search_template.triple(
        triple_source,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        triple_target)
    search_template.triple_with_relation(
        five_source,
        sc_types.EDGE_D_COMMON_VAR,
        five_target,
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        sc_types.UNKNOWN)

def unlink_ScTemplateResult(result:ScTemplateResult):
    client.delete_elements(result.get(1))

def delete_relation(rell:relation, keynodes:ScKeynodes):
    search_template = ScTemplate()

    if (isinstance(rell.src, str) and isinstance(rell.trg, str)):
        search_template.triple_with_relation(
            get_node_by_some_idtf(rell.src, keynodes),
            sc_types.EDGE_D_COMMON_VAR,
            get_node_by_some_idtf(rell.trg, keynodes),
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.UNKNOWN)
    else :
        if (isinstance(rell.src, list)):
            src_addr = get_node_by_some_idtf(rell.src[0], keynodes)
            fill_search_template(search_template,"_emptyNode", src_addr, "_emptyNode", get_node_by_some_idtf(rell.trg, keynodes))
        if isinstance(rell.trg, list) :
            trg_addr = get_node_by_some_idtf(rell.trg[0], keynodes)
            fill_search_template(search_template ,"_emptyNode", trg_addr, get_node_by_some_idtf(rell.src, keynodes), "_emptyNode")
    results = client.template_search(search_template)
    for result in results:
        unlink_ScTemplateResult(result)
   

def delete_all_relations(relations:set, keynodes:ScKeynodes):
      for relation in relations:
        delete_relation(relation, keynodes)

def add_sets_to_node(sets:Set, node:ScAddr, keynodes:ScKeynodes):
    for p_node in sets.parent:
        p_node_sc_sddr = get_node_by_some_idtf_or_create(p_node, False, keynodes)
        print("PARENT NODE::::::::::" + str(p_node_sc_sddr))
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,p_node_sc_sddr, node)
    for c_node in sets.child:
        c_node_sc_sddr = get_node_by_some_idtf_or_create(c_node, False, keynodes)
        print("CHILD NODE::::::::::" + str(c_node_sc_sddr))
        create_edge(sc_types.EDGE_ACCESS_CONST_POS_PERM,node, c_node_sc_sddr)

def delete_all_sets(sets:Set, node:ScAddr, keynodes:ScKeynodes):
    for child in sets.child :
        print ("CHIIIIIIIIIIIIILD")
        print (child)
        results = abstract_search_of_3iterator(node, get_node_by_some_idtf(child, keynodes))
        unlink_ScTemplateResult(results[0])
    for parent in sets.parent :
        print ("PAREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEENT")
        print (parent)
        print (get_node_by_some_idtf(parent, keynodes))
        results = abstract_search_of_3iterator(get_node_by_some_idtf(parent, keynodes), node)
        print(len(results))
        for result in results:
            unlink_ScTemplateResult(result)

def add_entity_to_kb(entity:entity, keynodes:ScKeynodes) :
    entity_node = get_node_by_some_idtf(entity.main_idtf, keynodes)
    print ("ENTITY_NOOOOOOOOOOOODE: "+ str(entity_node))
    if entity_node == None :
        entity_node = keynodes.resolve(entity.system_idtf, sc_types.NODE_CONST_CLASS)
        print ("ENTITY REEEEEEEEEEESOLVED: "+ str(entity_node))
        add_main_id_to_node(entity.main_idtf, entity_node , keynodes)
        add_relations_to_node(entity.relations, keynodes)
        add_sets_to_node(entity.sets, entity_node, keynodes)

def change_link_content(old_content: str, new_content: str):
    links =  client.get_links_by_content(old_content)[0]
    for link in links:
        link_content = ScLinkContent(new_content, ScLinkContentType.STRING)
        link_content.addr = link
        client.set_link_contents(link_content)

def delete_entity_from_kb(node:str, keynodes:ScKeynodes) :
    ent = get_entity_by_idtf(node, keynodes)
    addr = get_node_by_some_idtf(ent.main_idtf, keynodes)
    change_link_content(ent.main_idtf, "")
    change_link_content(ent.system_idtf, "")
    if client.delete_elements(addr):
        return ent
    else:
        return None

def get_difference(a:list[str], b:list[str]) -> set[str]:
    updated_set = set(a)
    old_set = set(b)
    return updated_set.difference(old_set)


def apply_changes(updated_node:entity, old_node:entity, keynodes:ScKeynodes):
    relations_to_add = get_difference(updated_node.relations, old_node.relations)
    relations_to_delete =  get_difference(old_node.relations, updated_node.relations)

    change_link_content(old_node.system_idtf, updated_node.system_idtf)
    change_link_content(old_node.main_idtf, updated_node.main_idtf)
    add_relations_to_node(relations_to_add, keynodes)
    delete_all_relations(relations_to_delete, keynodes)

    childs_to_add = get_difference(updated_node.sets.child, old_node.sets.child)
    childs_to_delete = get_difference(old_node.sets.child, updated_node.sets.child)

    parents_to_add = get_difference(updated_node.sets.parent, old_node.sets.parent)
    parents_to_delete = get_difference(old_node.sets.parent, updated_node.sets.parent)

    node_addr = get_node_by_some_idtf(updated_node.system_idtf, keynodes)
    add_sets_to_node(Set(parents_to_add, childs_to_add), node_addr, keynodes)
    delete_all_sets(Set(parents_to_delete, childs_to_delete), node_addr, keynodes)