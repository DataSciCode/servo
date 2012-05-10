import logging, re
from suds.client import Client
from suds.sudsobject import asdict
from servo3.models import GsxAccount
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

def looks_like(query, what = None):
  result = False
  
  if type(query) is not unicode:
    return False
  
  rex = {'partNumber': '^([a-z]{1,2})?\d{3}\-\d{4}$',\
    'serialNumber': '^[a-z0-9]{11,12}$',\
    'eeeCode': '^[A-Z0-9]{3,4}$',\
    'returnOrder': '^7\d{9}$',\
    'repairNumber': '^\d{12}$',\
    'dispatchId': '^G\d{9}$',\
    'alternateDeviceId': '^\d{15}$',\
    'diagnosticEventNumber': '^\d{23}$'}
  
  for k, v in rex.items():
    if re.search(v, query, re.IGNORECASE):
      result = k
  
  return (result == what) if what else result
  
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
  return [asdict(result.warrantyDetailInfo)]
  
def parts_lookup(query):
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
  
  if looks_like(query, "partNumber"):
    it.partNumber = query
  else:
    it = query
  
  req.lookupRequestData = it
  
  result = client.service.PartsLookup(req).parts
  
  if type(result) is not list:
    result = [result]
  
  results = []
  
  for i in result:
    results.append(asdict(i))
  
  return results
  