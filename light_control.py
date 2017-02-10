import appdaemon.appapi as appapi
import inspect
             
class light_control(appapi.AppDaemon):

  def initialize(self):
    self.log("lightcontrol")
    self.lights={"light.den_fan_light":{"default":"40","dim":"5"},
                 "light.outdoor_patio_light":{"default":"100","dim":"0"}}
                 
    self.rules={"light.den_fan_light":{"test":"media_player.dentv","rule":{"on":"dim","off":"default"}},
                "light.outdoor_patio_light":{"test":"sun.sun","rule":{"above_horizon":"dim","below_horizon":"default"}}}
                
    self.action={"sun":{"above_horizon":"off","below_horizon":"on"},
                 "switch":{"on":"on","off":"off"},
                 "light":{"on":"on","off":"off"},
                 "media_player":{"on":"on","off":"off"}}
    return              
    for entity in self.lights:
      self.listen_state(self.lightStateChange,entity)
      self.log("listen_state registered for {}".format(entity))
  
    for entity in self.rules:
      self.listen_state(self.testStateChanged,self.rules[entity]["test"])
      self.log("listen state registered for {}".format(self.rules[entity]["test"]))
      
  def lightStateChange(self,entity,attribute,old,new,kwargs):
    self.log("entity={}, attribute={} old={} new={} get_state returns={}".format(entity,attribute,old,new,self.get_state(entity)))
#    self.check_lights(entity,new)
    
  def check_lights(self,entity,new):
    self.log("entity={} new={}".format(entity,new))    
    if new=="on":
      self.log("entity={}  rules[entity]={}".format(entity,self.rules[entity]["test"]))
      runState=self.rules[entity]["rule"][self.get_state(self.rules[entity]["test"])]
      
      self.log("entity {} has turned on setting brightness to {}".format(entity,
               self.lights[entity][runState]))
      self.turn_on(entity,brightness=int(self.lights[entity][runState]))
    else:
      self.log("new={} so not doing anything".format(new))

  def testStateChanged(self,entity,attribute,old,new,kwargs):
    self.log("entity={} old={} new={} attribute={}".format(entity,old,new,attribute))
    if not old==new:
      for device in self.rules:
        self.log("device={}".format(device))
        if self.rules[device]["test"]==entity:
          self.log("entity={} device={} state={}".format(entity,device,self.get_state(device)))
          self.check_lights(device,self.get_state(device))

  def log(self,msg,level="INFO"):
    obj,fname, line, func, context, index=inspect.getouterframes(inspect.currentframe())[1]
    super(light_control,self).log("{} - ({}) {}".format(func,str(line),msg),level)

        
