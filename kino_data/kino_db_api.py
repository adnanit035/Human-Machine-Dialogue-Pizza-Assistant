"""
Created on Thu May 24 11:08:41 2018

@author: mahed
"""

def movie_producer(movie_title):
    movie_id_result = movie_id(movie_title)["movie_id"]
    request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id_result), THEMOVIEDB_API_KEY)
    raw = requests.get(request_url).json()
    mhd = {}
    for crew_element in raw["crew"]:
        if "Producer" == crew_element["job"]:
            mhd["celeb_name"] = crew_element["name"] 
            if crew_element["profile_path"] is not None:
                mhd["celeb_pic"] = THEMOVIEDB_IMAGE_PREFIX + crew_element["profile_path"]
            else:
                mhd["celeb_pic"] = DEFAULT_CELEB_PIC
            break
    query_function_res = query_function(movie_title)
    mhd["movie_title"] = query_function_res["movie_title"]
    if query_function_res["movie_pic"] is not None:
        mhd["movie_pic"] = THEMOVIEDB_IMAGE_PREFIX + query_function_res["movie_pic"]
    else:
        mhd["movie_pic"] = DEFAULT_MOVIE_PIC     
    mhd["voice"] = "The Producer of {} is {}.".format(query_function_res["movie_title"], mhd["celeb_name"])
    return mhd

def movie_writer(movie_title):
    movie_id_result = movie_id(movie_title)["movie_id"]
    request_url = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}".format(str(movie_id_result), THEMOVIEDB_API_KEY)
    raw = requests.get(request_url).json()
    mhd = {}
    people_list=[]
    for crew_element in raw["crew"]:
        celeb={}
        if "Writing" in crew_element["department"]:
            celeb['celeb_name']=crew_element["name"]
            if crew_element["profile_path"] is not None:
                 celeb['celeb_pic']=(THEMOVIEDB_IMAGE_PREFIX + crew_element["profile_path"])
            else:
                celeb['celeb_pic']=(DEFAULT_CELEB_PIC)
            celeb['celeb_role']=crew_element["job"]
            people_list.append(celeb)
    mhd["celeb_list"] = people_list
    celeb_name_list = []
    for celeb in mhd["celeb_list"]:
        celeb_name_list.append(celeb["celeb_name"])
    celeb_names_string = ""
    for celeb_name_index in range(0, len(celeb_name_list)):
        if celeb_name_index == 0:
            celeb_names_string += celeb_name_list[celeb_name_index]
        elif celeb_name_index != (len(celeb_name_list) - 1):
            celeb_names_string += ", {}".format(celeb_name_list[celeb_name_index])
        else:
            celeb_names_string += ", and {}".format(celeb_name_list[celeb_name_index])
    query_function_res = query_function(movie_title)
    mhd["movie_title"] = query_function_res["movie_title"]
    if query_function_res["movie_pic"] is not None:
        mhd["movie_pic"] = THEMOVIEDB_IMAGE_PREFIX + query_function_res["movie_pic"]
    else:
        mhd["movie_pic"] = DEFAULT_MOVIE_PIC
    mhd["voice"] = "{} has been written by {}.".format(query_function_res["movie_title"], celeb_names_string)
    return(mhd)