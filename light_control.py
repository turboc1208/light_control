import my_appapi as appapi
import inspect
             
class light_control(appapi.my_appapi):

  def initialize(self):
    self.log("lightcontrol")
    self.dim_rate=50   
    self.states={"on":["on","open","23","playing"],"off":["off","closed","22",0]}
    # Control_dict structure
    #"device:{ light : { "type": dimmer, ondevicestate: ondimmerstate, offdevicestate: "0"},
    #        { light : { "type": switch, "on": onswitchstate, "off": "off"}}

    self.control_dict={"light.den_fan_light":{"light.den_fan_light":{"type":"dimmer","on":"50","off":0,"last_brightness":""}},
                       "light.den_fan":{"light.den_fan":{"type":"dimmer","on":"50","off":0,"last_brightness":""}},
                       "switch.breakfast_room_light":{"switch.breakfast_room_light":{"type":"switch","on":"on","off":"off"}},
                       "light.office_lights":{"light.office_lights":{"type":"dimmer","on":"50","off":0,"last_brightness":""}},
                       "sensor.ge_32563_hinge_pin_smart_door_sensor_access_control_4_9":{"light.office_lights":{"type":"dimmer","on":"50","off":0,"last_brightness":""}},
                       "media_player.dentv":{"light.den_fan_light":{"type":"dimmer","on":"10","off":"last","last_brightness":""},
                                             "switch.breakfast_room_light":{"type":"switch","on":"off","off":"off"}},
                       "media_player.office_directv":{"light.office_lights":{"type":"dimmer","on":"10","off":"last","last_brigthness":""}},
                       "switch.downstairs_hallway_light":{"switch.downstairs_hallway_light":{"type":"switch","on":"on","off":"off"}},
                       "light.master_light_switch":{"light.master_light_switch":{"type":"dimmer","on":"255","off":0,"last_brightness":""}},
                       "binary_sensor.front_door_button_pressed":{"switch.front_door_light":{"type":"switch","on":"on","off":"delay"}} }

    for trigger in self.control_dict:
      self.listen_state(self.state_change,trigger,attributes="all")

    self.check_current_state()

  #########
  # Check_current_state - Initialization only
  #   Update current state of lights based on current state of triggers without waiting for trigger to be called
  #########
  def check_current_state(self):
    newstate={}
    for trigger in self.control_dict:
      dev,entity=self.split_entity(trigger)
      if dev in ["light","switch"]:                                              #if triggering device is a light or switch
        dev_state=self.get_state(trigger)                                        #get state of trigger
        for sublight in self.control_dict[trigger]:                              # for each light associated with trigger
          newstate[sublight]=self.control_dict[trigger][sublight][dev_state]       # add it's desired state to the list

    self.log("after first pass newstate={}".format(newstate))

    for trigger in self.control_dict:                                            # loop through again
      dev,entity=self.split_entity(trigger)
      if dev not in ["light","switch"]:                                          # if trigger is not a light or a switch like a TV or doorbell
        dev_state=self.get_state(trigger)
        for sublight in self.control_dict[trigger]:                                 # loop through sublights
          newstate[sublight]=self.control_dict[trigger][sublight][self.convert_dev_state(dev_state)]   # determine new state of the sublight not sure why we did this in two loops.
    self.log("after second pass newstate={}".format(newstate))

    for light in newstate:                                         # cycle through the lights setting states
      if newstate[light] in self.states["on"]:                     # if the new state is on 
        self.log("Turning {} on".format(light))
        self.turn_on(light)                                           # turn on the light
      elif newstate[light] in self.states["off"]:                  # else if it's off
        self.log("Turning {} off".format(light))
        self.turn_off(light)                                          # turn off the light
      elif newstate[light]=="dim":                                 # else if it's dim
        self.log("Dimming {}".format(light))
        self.run_in(self.dim_light,600,light=light)                   # check again in 10 minutes to start diming again if spot is done
      elif newstate[light]=="last":                                # else if it's last
        self.log("dont know last value for {} leaving it alone".format(light))   # since this is in initialize, just leave last alone because we don't know what it is now.
        continue
      else:                                                        # else lets just try setting the light level to it in hopes it's a number.
        try:
          dimamt=int(newstate[light])
        except ValueError:                                         # it's not a number.
          self.log("invalid new light state {}".format(newstate[light]))
          continue
        except:
          raise
                                       
        if dimamt==0:                                              # it's a number so if the dim level is 0 then turn off the light
          self.log("turning off dimmer {}".format(light))
          self.turn_off(light)
        else:                                                      # else just dim by dimat value.
          self.log("setting {} to {} brightness".format(light,dimamt))
          self.turn_on(light,brightness=dimamt)

  #############
  #
  # convert_dev_state - normalizes state to an on or off value
  #############
  def convert_dev_state(self,state):
    newstate=""
    if state in self.states["on"]:
      newstate="on"
    elif state in self.states["off"]:
      newstate= "off"
    else :
      newstate= state      # we don't know what the state is to normalize it so it's a unique value lets just return it
    return newstate

  ########
  # state_changed - handler for state changes
  ########
  def state_change(self,trigger,attributes,old,new,kwargs):
    self.log("old = {} new= {}".format(old,new))
    if not ((old==new) or (new=="unavailable")):     # control entity changed state
      for light in self.control_dict[trigger]:            # loop through lights controled by control entity
        self.set_light_state(trigger,light,new)


  def set_light_state(self,trigger,light,trigger_state):
    self.log("light {}, self.control_dict[trigger][light] {}, trigger_state {} - {}".format(light,self.control_dict[trigger][light],trigger_state,self.convert_dev_state(trigger_state)))
    if self.control_dict[trigger][light][self.convert_dev_state(trigger_state)] in self.states["off"]:         # if new desired state is off
      self.log("New desired state is {}".format(self.control_dict[trigger][light][self.convert_dev_state(trigger_state)]))
      self.log("turn off the light regardless of anything else")
      self.turn_off(light)
    elif self.control_dict[trigger][light][self.convert_dev_state(trigger_state)]=="delay":
      self.log("turning off {} in 30 seconds".format(light))
      self.turn_off_in(light,900)
    elif self.control_dict[trigger][light][self.convert_dev_state(trigger_state)]=="last":       # new desired state is on or last
      self.log("last")
      if self.get_state(light,attribute="state") in self.states["on"]:                             # if current state is on
        dev, name=self.split_entity(light)
        if dev=="light"                                        :                                     # is this a light (lights are dimable and have a last_brightness attribute)
          if not self.control_dict[trigger][light]["last_brightness"]=="":                                # is there a value for last brightness
            self.log("returning {} to previous state brightness {}".format(light,self.control_dict[trigger][light]["last_brightness"]))
            self.turn_on(light,brightness=self.control_dict[trigger][light]["last_brightness"])              # yes and the light was on so adjust the brightness
            self.control_dict[trigger][light]["last_brightness"]=""                                          # clear last brightness we are done with it
          else:                                                                                          # there wasn't a value for last brightness
            self.log("no previous light level must have been off")
            self.turn_off(light)                                                                            # turn light off
        else:                                                                                         # light is  a switch 
          self.log("switch so last makes no sense")
          self.turn_off(light)                                                                           # turn if off
      else:                                                                                        # current state is off and desired state is off
        self.log("light is off leave it that way")                                                   # light wasn't on in the first place so don't do anything
    elif self.control_dict[trigger][light][self.convert_dev_state(trigger_state)]=="dim":         # if the new state = dim  - this is to handle dimming lights over time
      self.log("dim light {} till it's off".format(light))
      if self.get_state(light,attribute="state") in self.states["on"]:                            # check if the light is on
        self.run_in(self.dim_light,60,light=light)                                                  # schedule a call back to dim the light some
    else:                                                                                       # else only other option is the desired state = on
      self.log("New desired state for {} is on or has a dimmmer value {}".format(light,self.control_dict[trigger][light][self.convert_dev_state(trigger_state)]))
      if self.get_state(light,attribute="state") in self.states["on"]:                            # if the current state is on and desired state is on
        self.log("{}'s current state is on".format(light))                                          # light is already on
        if self.control_dict[trigger][light]["type"]=="dimmer":                                      # if light is a dimmer
          self.log("{} is a currently on dimmer seting value to {} ".format(light,self.control_dict[trigger][light][self.convert_dev_state(trigger_state)]))
          self.control_dict[trigger][light]["last_brightness"]=self.get_state(light,attribute="brightness") # save the current brightness
          if self.control_dict[trigger][light][self.convert_dev_state(trigger_state)] == "on":         # if new state = on  
            self.turn_on(light)                                                                          # turn on light 
          else:                                                                                        # value given to dim to, so dim to that value
            self.turn_on(light,brightness=self.control_dict[trigger][light][self.convert_dev_state(trigger_state)])  # turn on the light at the given brightness
        else:                                                                                       # else we are not a dimmer
          self.log("{} is a currently on switch".format(light))
          self.turn_on(light)                                                                       # light is a switch so just turn it on
      else:                                                                                       # light is off but desired state is on
        if trigger==light:                                                                        # is the trigger controlling itself
          if self.control_dict[trigger][light]["type"]=="dimmer":                                      # if light is a dimmer
            self.log("{} is a currently off Dimmer".format(light))                                      
            self.turn_on(light,brightness=self.control_dict[trigger][light][self.convert_dev_state(trigger_state)])  # light is currently off so just turn it on at designated brightness
          else:                                                                                       # else light is not a dimmer
            self.log("{} is a currently off switch".format(light))
            self.turn_on(light)                                                                        # light is currently off, so just turn it on
        else:
          self.log("Trigger {} turned on, but light {} is off so leaving it off".format(trigger,light))
    self.log("the end of set_light_state")

  def dim_light(self,kwargs):
    light=kwargs.get("light",None)
    self.log("dimming light={}".format(light))
    if self.get_state(light) in self.states["on"]:
      devtypes=["light","switch"]
      spot_lights=self.build_entity_list("group.app_spotcontrol_spots_lights",devtypes)
      if not ((self.get_state("input_boolean.spot") in self.states["on"]) and (light in spot_lights)):   # are we dealing with an exception (spot cleaning)
        current_brightness=self.get_state(light,"brightness")
        if current_brightness>=self.dim_rate:                                         # not an exception, is the light still bright enough to see
          self.turn_on(light,brightness= current_brightness-self.dim_rate) # yes, so dim it somemore
          self.log("new brightness={}".format(self.get_state(light,"brightness")))
          self.run_in(self.dim_light,300,light=light)                                      # schedule to run again
        else:
          self.turn_off(light)                                                            # to dim to see so turn it off
      else:                                                                               # else this is an exception (spot cleaning)
        self.log("exception spot is cleaning")
        self.turn_on(light,brightness=255)
        self.log("returning to full brightness")
        self.run_in(self.dim_light,600,light=light)                                       # check again in 10 minutes to start diming again if spot is done
    else:
      self.log("light is finally off don't schedule anymore checks")
    
