import appdaemon.appapi as appapi
import inspect
             
class light_control(appapi.AppDaemon):

  def initialize(self):
    self.log("lightcontrol")
   
#    self.light_states={"light.den_fan_light":{"type":"dimmer","on":"50","off":"0","dim":"10"},
#                       "light.outdoor_patio_light":{"type":"dimmer","on":"100","off":"0"}}

                      #"device:{ light : { "type": dimmer, ondevicestate: ondimmerstate, offdevicestate: "0"},
                      #        { light : { "type": switch, "on": onswitchstate, "off": "off"}}

    self.control_dict={"light.den_fan_light":{"light.den_fan_light":{"type":"dimmer","on":"50","off":"0"}},
                       "switch.breakfast_room_light":{"switch.breakfast_room_light":{"type":"switch","on":"on","off":"off"}},
                       "media_player.dentv":{"light.den_fan_light":{"type":"dimmer","on":"10","off":"0"},
                                             "switch.breakfast_room_light":{"type":"switch","on":"off","off":"off"}},
                       "light.outdoor_patio_light":{"light.outdoor_patio_light":{"type":"dimmer","on":"100","off":"0"}} }

    for control in self.control_dict:
      self.listen_state(self.state_change,control,attributes="all")

  def state_change(self,entity,attributes,old,new,kwargs):
    if not old==new:
      self.log("entity={}, old={}, new={}, attributes={}".format(entity,old,new,attributes))
      if new=="on":
        self.log("entity {} turned {}".format(entity,new))
        for light in self.control_dict[entity]:
          self.log("light {} is a {}. Turning light {}".format(light,self.control_dict[entity][light]["type"],self.control_dict[entity][light][new]))
          light_type=self.control_dict[entity][light]["type"]
          if light_type=="dimmer":
            brightness=self.control_dict[entity][light][new]
            if brightness==0:
              self.turn_off(light)
            else:
              self.log("light={} brightness={}".format(light,self.control_dict[entity][light]["on"]))
              self.turn_on(light,brightness=self.control_dict[entity][light]["on"])
          else:
            self.log("do something witha switch")
            
