from models import Project

def get_projects_with_scraplists( user, scrapslength=5 ):
    """Returns a set of dicts, each containing useful information, a short set of scraps, and the number of remaining scraps"""
    
    projects = []
    
    for project_entity in Project.all().filter('user =', user).order("-updated"):
        
        scraps = project_entity.scrap_set.order("-created")
        scraps_count = scraps.count()
        scraps_remainder = scraps_count-scrapslength if scraps_count>=scrapslength else 0

        projects.append( {'name':project_entity.name, 'scraps':scraps.fetch(scrapslength), 'id':project_entity.key().id(), 'remainder':scraps_remainder} )
        
    return projects