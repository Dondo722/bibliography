from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *

from .ostis import get_entity_by_idtf, add_entity_to_kb,delete_entity_from_kb, apply_changes
from .models import entity
from sc_kpm import ScKeynodes

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class EntityProvider(APIView):

    def get(self, request, node):
        try: 
            keynodes = ScKeynodes()
            ent = get_entity_by_idtf(node, keynodes)
            print(f"{bcolors.WARNING}GET_GET_GET_GET_GET{bcolors.ENDC}")
            print ("ENTITY::::::::::::::::::")
            print(ent)
            JSON_ent = entity.obj_2_json(ent)
            print ("JSON::::::::::::::::::")
            print(JSON_ent)
            return Response(JSON_ent)
        except Exception:
            return Response(status=HTTP_418_IM_A_TEAPOT)

    def post(self, request):
        try: 
            keynodes = ScKeynodes()
            print(f"{bcolors.HEADER}POST_POST_POST_POST{bcolors.ENDC}")
            ent = entity.from_json(request)
            print(ent)
            JSON_ent = entity.obj_2_json(ent)
            print ("JSON::::::::::::::::::")
            add_entity_to_kb(ent, keynodes)
            return Response(JSON_ent)
        except Exception:
            return Response(status=HTTP_418_IM_A_TEAPOT)

    def delete(self, request, node):
            keynodes = ScKeynodes()
            ent = delete_entity_from_kb(node, keynodes)
            print(f"{bcolors.WARNING}GET_GET_GET_GET_GET{bcolors.ENDC}")
            print ("ENTITY::::::::::::::::::")
            print(ent)
            JSON_ent = entity.obj_2_json(ent)
            print ("JSON::::::::::::::::::")
            print(JSON_ent)
            return Response(JSON_ent)

    def patch(self, request):
        keynodes = ScKeynodes()
        old_ent = get_entity_by_idtf(request.data["original_sytem_idtf"], keynodes)
        if (old_ent == None) :
            return Response(status=HTTP_418_IM_A_TEAPOT)
        try: 
            new_ent = entity.from_json(request)
            apply_changes(new_ent, old_ent, keynodes)
            print("NEW")
            print(new_ent)
            print("OLD")
            print(old_ent)
            JSON_ent = entity.obj_2_json(new_ent)
            return Response(JSON_ent)
        except Exception:
            return Response(status=HTTP_418_IM_A_TEAPOT)
