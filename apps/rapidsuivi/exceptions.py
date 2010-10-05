from django.utils.translation import  ugettext_lazy  as _
class VillageNotExistError (Exception):
	"""Le village n'existe pas encore dans la base de donnee """
	def __init__(self):
		super(VillageNotExistError , self).__init__()
		
class RelayNotExistError (Exception):
	"""Le relay n'existe pas encore"""
	def __init__(self):
		super (RelayNotExistError, self).__init__()
		
class ObjectExistError(Exception):
	def __init__(self):
		super (ObjectExistError ,self).__init__()
		
class RelayExistError (ObjectExistError):
	  """
	  Le relay existe deja dans la base de donnees
	  """
	  def __init__(self):
	  	    super (RelayExistError , self).__init__()
	  	    
	
		 
		
	
	
	