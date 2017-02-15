import appdaemon.appapi as appapi
import inspect
             
class light_control(appapi.AppDaemon):

  def initialize(self):
    self.log("lightcontrol")
   
    # Control_dict structure
    #"device:{ light : { "type": dimmer, ondevicestate: ondimmerstate, offdevicestate: "0"},
    #        { light : { "type": switch, "on": onswitchstate, "off": "off"}}

    self.control_dict={"light.den_fan_light":{"light.den_fan_light":{"type":"dimmer","on":"50","off":"0","last_brightness":""}},
                       "switch.breakfast_room_light":{"switch.breakfast_room_light":{"type":"switch","on":"on","off":"off"}},
                       "media_player.dentv":{"light.den_fan_light":{"type":"dimmer","on":"10","off":"last","last_brightness":""},
                                             "switch.breakfast_room_light":{"type":"switch","on":"off","off":"on"}},
                       "light.outdoor_patio_light":{"light.outdoor_patio_light":{"type":"dimmer","on":"100","off":"0","last_brightness":""}} }

    for control in self.control_dict:
      self.listen_state(self.state_change,control,attributes="all")

  def state_change(self,entity,attributes,old,new,kwargs):
    if not old==new:     # control entity changed state
      for light in self.control_dict[entity]:            # loop through lights controled by control entity
        self.set_light_state(entity,light,new)


  def set_light_state(self,entity,light,entity_state):
    self.log("light {}, self.control_dict[entity][light] {}, entity_state {}".format(light,self.control_dict[entity][light],entity_state))
    if self.control_dict[entity][light][entity_state]=="off":                                              # new desired state is off
      self.log("New desired state is {}".format(self.control_dict[entity][light][entity_state]))
      self.log("turn off the light regardless of anything else")
      self.turn_off(light)
    elif self.control_dict[entity][light][entity_state]=="last":
      if self.get_state(light,attribute="state")=="on":
        if not self.control_dict[entity][light]["last_brightness"]=="":
          self.log("returning {} to previous state brightness {}".format(light,self.control_dict[entity][light]["last_brightness"]))
          self.turn_on(light,brightness=self.control_dict[entity][light]["last_brightness"])
          self.control_dict[entity][light]["last_brightness"]=""
        else:
          self.log("no previous light level must have been off")
          self.turn_off(light)
      else:
        self.log("light is off leave it that way")
    else:
      self.log("New desired state is on or has a dimmmer value {}".format(self.control_dict[entity][light][entity_state]))
      if self.get_state(light,attribute="state")=="on":
        self.log("current state is on")
        if self.control_dict[entity][light]["type"]=="dimmer":
          self.log("light is a currently on dimmer seting value to {} ".format(self.control_dict[entity][light][entity_state]))
          self.control_dict[entity][light]["last_brightness"]=self.get_state(light,attribute="brightness")
          self.turn_on(light,brightness=self.control_dict[entity][light][entity_state])
        else:
          self.log("Light is a currently on switch")
          self.turn_on(light)
      else:
        if self.control_dict[entity][light]["type"]=="dimmer":
          self.log("light is a currently off Dimmer")
          self.turn_off(light)
        else:
          self.log("light is a currently off switch")
          self.turn_off(light)
      
