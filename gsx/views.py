import logging
from suds.client import Client
from suds.sudsobject import asdict
from servo3.models import GsxAccount
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

def warranty_status(sn):
  """
  docstring for warranty_status
  """
  act = GsxAccount.objects.first()
  client = Client("https://gsxwsit.apple.com/wsdl/amAsp/gsx-amAsp.wsdl")
  
  req = client.factory.create('ns3:AuthenticateRequest')
  req.serviceAccountNo = act.sold_to
  req.userId = act.username
  req.password = act.password
  req.languageCode = "en"
  req.userTimeZone = "CEST"
  
  session = client.service.Authenticate(req)
  
  req = client.factory.create('ns3:warrantyStatusRequestType')
  ud = client.factory.create('ns7:unitDetailType')
  ud.serialNumber = sn
  req.unitDetail = ud
  req.userSession = session

  result = client.service.WarrantyStatus(req)
  return asdict(result.warrantyDetailInfo)
  
def parts_lookup(number):
  """
  docstring for parts_lookup
  """
  act = GsxAccount.objects.first()
  client = Client("https://gsxwsit.apple.com/wsdl/amAsp/gsx-amAsp.wsdl")
  
  req = client.factory.create('ns3:AuthenticateRequest')
  req.serviceAccountNo = act.sold_to
  req.userId = act.username
  req.password = act.password
  req.languageCode = "en"
  req.userTimeZone = "CEST"
  
  session = client.service.Authenticate(req)
  
  req = client.factory.create('ns0:partsLookupRequestType')
  req.userSession = session
  it = client.factory.create('ns7:partsLookupInfoType')
  it.partNumber = number
  req.lookupRequestData = it
  
  result = client.service.PartsLookup(req).parts
  return [asdict(result)]
  
def looks_like(what):
  pass
  