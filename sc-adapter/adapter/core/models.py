from django.db import models
from rest_framework import serializers

class Set:
    parent: list[str]
    child: list[str]

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    def __str__(self) -> str:
        str_of_parent = ""
        for nodes in self.parent:
            str_of_parent +=  nodes + " "
        str_of_child = ""
        for nodes in self.child:
            str_of_child +=  nodes + " "
        return "parent: " + str_of_parent + "\n" + " child: " + str_of_child 
        
    
    def obj_2_json(obj) :
        return {
            "parent" : obj.parent,
            "child" : obj.child,
        }
    
    def from_json(obj:dict) :
        return Set(
            parent=obj.get("parent"),
            child=obj.get("child"))


class relation:
    src: str
    trg: str
    name: str

    def __init__(self, src:str, trg:str, name:str):
        self.src = src
        self.trg = trg
        self.name = name

    def __str__(self) -> str:
         return str(self.src) + " = " + str(self.name) + " => " + str(self.trg) 

    def compare_list_or_string(self, first, second) -> bool:
        is_equals = True
        if isinstance(first, list) and isinstance(second, list) :
            a = set(first)
            b = set(second)
            a_b_diff = a.difference(b)
            b_a_diff = b.difference(a)
            if (len (a_b_diff) != 0 or len(b_a_diff) != 0) :
                is_equals = False
        elif isinstance(first, str) and isinstance(second, str) :
            if (first.strip() != second.strip()) :
                is_equals = False
        else :
            is_equals = False
        return is_equals

    def __eq__(self, __o: object) -> bool:
        return  self.compare_list_or_string(self.src, __o.src) and self.compare_list_or_string(self.trg, __o.trg) and self.compare_list_or_string(self.name,__o.name)

    def __hash__(self) -> int:
        return hash(self.name.strip()) 

    def obj_2_json(obj) :
        return {
            "src" : obj.src,
            "trg" : obj.trg,
            "name" : obj.name
        }

    def from_json(obj:dict) :
        return relation (
            src= obj.get("src"), 
            trg=obj.get("trg"), 
            name=obj.get("name"))


class entity():
    main_idtf: str
    system_idtf: str
    relations: list[relation]
    sets: Set

    def __init__(self,system_idtf, main_idtf, relations, sets):
        self.system_idtf = system_idtf
        self.main_idtf = main_idtf
        self.relations = relations
        self.sets = sets

    def __str__(self) -> str:
        rrels = ''
        for rel in self.relations:
            rrels += str(rel) + "\n"
        return "main_idtf  " +  self.main_idtf + "\n" + "system_idtf " + self.system_idtf + "\n" + "relations " + rrels + "\n" + "sets " + str(self.sets)
            
    def obj_2_json(obj) :
        if (obj == None) :
            return {
            "main_idtf" : None,
            "system_idtf" : None,
            "relations" : None,
            "sets" : None
            }
        relations = {}
        id = 0
        for rel in obj.relations:
            relations.update({id : relation.obj_2_json(rel)})
            id += 1

        return {
            "main_idtf" : obj.main_idtf,
            "system_idtf" : obj.system_idtf,
            "relations" : relations,
            "sets" : Set.obj_2_json(obj.sets)
        }

    def from_json(request):
        dict_relations = request.data["relations"]
        list_relations =  list(dict_relations.values())
        mapped_relations = []

        for rel in list_relations:
            mapped_relations.append(relation.from_json(rel))

        dict_sets = request.data["sets"]
        return entity (
            main_idtf=request.data["main_idtf"],
            system_idtf=request.data["system_idtf"],
            relations=mapped_relations,
            sets= Set.from_json(request.data["sets"])
        )