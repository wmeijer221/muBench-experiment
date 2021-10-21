import random
import os

WORKMODEL_PATH = os.path.dirname(os.path.abspath(__file__))


# Select exactly one service function according to the probability
# Get in INPUT the list with the internal-service functions
def select_internal_service(internal_services):
    internal_service_items = internal_services.items()
    random_extraction = random.random()
    # print("Extraction: %.4f" % random_extraction)
    p_total = 0.0
    for v in internal_services.values():
        p_total += v["probability"]
    p_total = round(p_total, 10)
    prev_interval = 0
    for k in internal_services.keys():
        if random_extraction <= prev_interval + internal_services[k]["probability"]/p_total:
            function_id = k       
            return function_id
        prev_interval += round(internal_services[k]["probability"]/p_total, 10)


def get_work_model(service_mesh, workmodel_params):
    work_model = dict()
    
    if "override" in workmodel_params.keys():
        override = workmodel_params["override"]["value"]
    else:
        override = dict()
    
    request_method = workmodel_params["request_method"]["value"]
    databases_prefix = workmodel_params["databases_prefix"]["value"]


    internal_services = dict()
    internal_services_db = dict()

    for k in workmodel_params.keys():
        w=workmodel_params[k]
        if w["type"]!="function":
            continue
        tmp_dict=dict() # string to be inserted as internal service in workmodel.json if this function is chosen 
        tmp_dict.update({"internal_service": {w["value"]["name"]: w["value"]["parameters"]}})
        tmp_dict.update({"request_method": request_method})
        tmp_dict.update({"workers": w["value"]["workers"]})
        tmp_dict.update({"threads": w["value"]["threads"]})  
        if "recipient" in w["value"] and w["value"]["recipient"] == "database":
            internal_services_db[k]=dict()
            internal_services_db[k].update({"string" : tmp_dict})
            internal_services_db[k].update({"probability": w["value"]["probability"]})
        elif "recipient" in w["value"] and w["value"]["recipient"] == "service":
            internal_services[k]=dict()
            internal_services[k].update({"string" : tmp_dict})
            internal_services[k].update({"probability": w["value"]["probability"]})
    if len(internal_services_db) == 0:
        internal_services_db = internal_services
    try:
        for vertex in service_mesh.keys():
            work_model[f"{vertex}"] = {'external_services':service_mesh.get(vertex)['external_services']}
            
            if vertex.startswith(databases_prefix):
                selected_internal_service = select_internal_service(internal_services_db)
                work_model[f"{vertex}"].update(internal_services_db[selected_internal_service]['string'])
            else:
                selected_internal_service = select_internal_service(internal_services)
                work_model[f"{vertex}"].update(internal_services[selected_internal_service]['string'])
            
            if vertex in override.keys():
                if "sidecar" in override[vertex].keys():
                    work_model[f"{vertex}"].update({"sidecar": override[vertex]["sidecar"]})
                if "function_id" in override[vertex].keys():
                    work_model[f"{vertex}"].update(internal_services[override[vertex]['function_id']]['string'])
                    continue
      

    except Exception as err:
        print("ERROR: in get_work_model,", err)
        exit(1)
    
    print("Work Model Created!")
    return work_model
