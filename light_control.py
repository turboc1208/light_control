##############
#  Light_Control
#  Author: Chip Cox
#  
#  Version    Date        Name      description
#  0.1.0      10APR2017   Chip Cox  Initial Development Completed
#
#  Light Control is goverened by a dictionary structure shown below
#
# Control_dict structure
#"trigger":{ "target" : { "On_Trigger_state": "target_state", "Off_Trigger_State": "target_state"},
#          { "target" : { "on"              : "on"          , "off"              : "off"}
#"time":{"19:00:00":{"light.front_porch_lights":{"state":"on","dow":"m,t,w,th,f"},
#                    "switch.back_porch_light":{"state":"on","dow":"all"}},
#        "23:30:00":{"switch.back__porch_light":{"state":"off","dow":"all"}}}}
#
# Triggers represent the action that causes an action to be performed against a target
# Trigger_State - the new state the trigger transitioned to that is causing the event.  A trigger state is either on or off, 
# On_Trigger_state - typically a litereal "on"
# Off_Trigger_state - typically a ligerall "off"
# target_state - the new state target should be moved to depending on the on/off_trigger_state
# Target represents the light or switch that is turned on/off depending on the new trigger_state
#
# For example, if we want to turn on the entry_way_light when the door_bell is pushed we might have the following.
# trigger = sensor.door_bell
# target = switch.entry_way_light
# in response to the ON trigger state we set the target state to ON
# 
# "sensor.door_bell":{"switch.entry_way_light":{"on":"on", "off":"ignore"}}
# 
# if we want an action performed on more than one target, just include a second target dictionary under the trigger dictionary.
#
# "sensor.door_bell":{"switch.entry_way_light":{"on":"on", "off":"ignore"},
#                    {"light.front_porch_light":{"on":"on", "off":"ignore"}}
#
# There are seceral different target_actions that can be performed.
# on - turn the target on
# off - turn the target off
# number - set the target light (dimmer) to number brightness (0 - 255)
# delay - "delay,state,seconds" - "delay, on, 300" delays turning on the target for 300 seconds.
# ignore - do nothing - for example, since a doorbell is a momentart contact device, it turns off as soon as it turns on,
#                       so you may want to do something on the "on" trigger, but ignore the "off" trigger and just leave the light on.
# 
# There are a couple of different types of triggers.
# object triggers where a doorbell or opening a door or turning on a light causes an action in another device.
# sun based triggers are really object triggers where sun.sun is the object.  above_horizon is considered on the sun is on, 
#                                                                              below_horizon is considered off the sun is off
# time triggers execute at a specific time every day.  when the trigger activates it checks the dow to see if it should run that day or not.
##############
import my_appapi as appapi
import inspect
             
class light_control(appapi.my_appapi):

  def initialize(self):
    self.log("lightcontrol")
    self.dim_rate=50   
    self.dow_map=["M","T","W","TH","F","S","SU"]
    self.states={"on":["on","open","23","playing","Home","house","above_horizon"],
                 "off":["off","closed","22",0,"0",
                        "not_home","Academy","Bayer","Corporate",                # handle non-home zones
                        "covington pike","frayser","Macon Rd","MBA",             # non-home zones
                        "Quince","southhaven","Spottswood","UOM",                # non-home zones
                        "Winchester",                                            # non-home zones
                        "None","below_horizon"]}
    # Control_dict structure
    #"trigger":{ "target" : { "On_Trigger_state": "target_state", "Off_Trigger_State": "target_state"},
    #          { "target" : { "on"              : "on"          , "off"              : "off"}}

    self.control_dict={"light.den_fan_light":{"light.den_fan_light":{"on":"50","off":"0","last_brightness":""}},
                       "light.den_fan":{"light.den_fan":{"on":"50","off":"0","last_brightness":""}},
                       "switch.breakfast_room_light":{"switch.breakfast_room_light":{"on":"on","off":"off"}},
                       "light.office_lights":{"light.office_lights":{"on":"50","off":"0","last_brightness":""}},
                       "light.office_fan":{"light.office_fan":{"on":"128","off":"0","last_brightness":""}},
                       "sensor.ge_32563_hinge_pin_smart_door_sensor_access_control_4_9":{"light.office_lights":{"on":"50","off":"0","last_brightness":""}},
                       "media_player.dentv":{"light.den_fan_light":{"on":"10","off":"last","last_brightness":""},
                                             "switch.breakfast_room_light":{"on":"off","off":"on"}},
                       "media_player.office_directv":{"light.office_lights":{"on":"10","off":"last","last_brigthness":""}},
                       "switch.downstairs_hallway_light":{"switch.downstairs_hallway_light":{"on":"on","off":"off"}},
                       "switch.carriage_lights":{"switch.carriage_lights":{"on":"on","off":"off"}},
                       "sun.sun":{"switch.carriage_lights":{"on":"off","off":"on"}},
                       "light.master_light_switch":{"light.master_light_switch":{"on":"255","off":"0","last_brightness":""}},
                       "light.shed_lights":{"light.shed_lights":{"on":"255","off":"0","last_brightness":""}},
                       "light.shed_flood_light":{"light.shed_flood_light":{"on":"255","off":"0","last_brightness":""}},
                       "device_tracker.scox0129_sc0129":{"switch.downstairs_hallway_light":{"on":"on","off":"ignore"},
                                                         "light.sam_light_switch":{"on":"ignore","off":"0","last_brightness":""},
                                                         "light.sam_fan_switch":{"on":"ignore","off":"0","last_brightness":""},
                                                         "switch.sam_toilet_fan":{"on":"ignore","off":"0"},
                                                         "switch.sam_toilet_light":{"on":"ignore","off":"0"},
                                                         "switch.sam_vanity_switch":{"on":"ignore","off":"0"}},
                       "light.sam_light_switch":{"light.sam_light_switch":{"on":"255","off":"0","last_brightness":""}},
                       "light.sam_fan_switch":{"light.sam_fan_switch":{"on":"128","off":"0","last_brightness":""}},
                       "device_tracker.ccox0605_ccox0605":{"switch.downstairs_hallway_light":{"on":"on","off":"ignore"},
                                                           "light.charlie_light_switch":{"on":"ignore","off":"0","last_brightness":""},
                                                           "light.charlie_fan_switch":{"on":"255","off":126,"last_brightness":""}},
                       "light.charlie_light_switch":{"light.charlie_light_switch":{"on":"255","off":"0","last_brightness":""}},
                       "light.charlie_fan_switch":{"light.charlie_fan_switch":{"on":"128","off":"0","last_brightness":""}},
                       "group.app_light_control_master":{"light.master_light_switch":{"on":"ignore","off":"0","last_brightness":""},
                                                         "light.master_fan":{"on":"ignore","off":"0","last_brightness":""},
                                                         "light.master_floor_light":{"on":"ignore","off":"0","last_brightness":""},
                                                         "switch.master_toilet_fan":{"on":"ignore","off":"0"},
                                                         "switch.master_toilet_light":{"on":"ignore","off":"0"}},
                       "device_tracker.scox1209_scox1209":{"switch.downstairs_hallway_light":{"on":"on","off":"ignore"}},
                       "device_tracker.turboc1208_cc1208":{"switch.downstairs_hallway_light":{"on":"on","off":"ignore"}},
                       "light.master_floor_light":{"light.master_floor_light":{"on":"128","off":"0","last_brightness":""}},
                       "switch.master_toilet_light":{"switch.master_toilet_fan":{"on":"delay,on,300","off":"delay,off,300"}},
                       "switch.half_bath_light":{"switch.half_bath_fan":{"on":"delay,on,30","off":"delay,off,30"}},
                       "switch.sam_toilet_light":{"switch.sam_toilet_fan":{"on":"delay,on,300","off":"delay,off,300"}},
                       "input_boolean.spot":{"switch.kitchen_overhead_light":{"on":"on","off":"off"},
                                             "light.stairway_light_switch":{"on":"255","off":"0","last_brightness":""},
                                             "switch.downstairs_hallway_light":{"on":"on","off":"off"}},
                       "time":{"15:50:00":{"light.front_porch_lights":{"state":"on","dow":"m,t,w,th,f"},
                                           "switch.back_porch_light":{"state":"on","dow":"all"}},
                               "23:30:00":{"switch.back__porch_light":{"state":"off","dow":"all"}}},
                       "binary_sensor.ring_front_door_ding":{"switch.front_door_light":{"on":"on","off":"delay,off,900"}} }

    #self.log("group.app_light_control_master = {}".format(self.get_state("group.app_light_control_master")))

    self.direct_light_control=["switch","light","sensor","binary_sensor","input_boolean"]

    for trigger in self.control_dict:
      if trigger=="time":
        for runtime in self.control_dict[trigger]:
          for target_entity in self.control_dict[trigger][runtime]:
            self.log("scheduling {} to turn {} at {} on {} days".format(target_entity,self.control_dict[trigger][runtime][target_entity]["state"],
                                                                        runtime,self.control_dict[trigger][runtime][target_entity]["dow"]))
            self.run_daily(self.timer_handler,self.parse_time(runtime),target_entity=target_entity,target_state=self.control_dict[trigger][runtime][target_entity]["state"],
                                                                       dow=self.control_dict[trigger][runtime][target_entity]["dow"])
      else:
        self.listen_state(self.state_change,trigger,attributes="state")

  #############
  #
  # timer_handler - handle callback from time scheduled events
  #
  #############
  def timer_handler(self,kwargs):
    currentdow=self.dow_map[self.datetime().today().weekday()]

    # If trigger is included in kwargs we want to check and make sure the previous trigger state is still the same if not, the dont do anything
    # for example if you turn on the bathroom light an event to turn on the fan is immediatly issued. 
    # when the fan start time comes though, if the light has already been turned off, then we don't want to start the fan
    # we only want to start the fan if the light is still on.

    if "trigger" in kwargs:    # this is just for error checking, but is why we have to have the return in this block instead of making it pretty
      if not kwargs["trigger_state"]==self.get_state(kwargs["trigger"],attribute="state"):
        self.log("trigger {} state changed not turning {} {}".format(kwargs["trigger"],kwargs["target_entity"],kwargs["target_state"]))
        return      # I hate having this return here, but it really avoids duplicate code for the next section.
    elif not ((currentdow.upper() in kwargs["dow"].upper().split(",")) or (kwargs["dow"].upper()=="ALL")):
      self.log("today {} is not in authorized dow {}".format(currentdow.upper(),kwargs["dow"].upper()))
      return

    if kwargs["target_state"]=="on":
      self.turn_on(kwargs["target_entity"])
    else:
      self.turn_off(kwargs["target_entity"])

  #############
  #
  # convert_dev_state - normalizes state to an on or off value
  #############
  def convert_dev_state(self,state):
    newstate=""
    if state in self.states["on"]:
      newstate="on"
    elif (state in self.states["off"]) or (state=="0"):
      newstate= "off"
    else :
      newstate= state      # we don't know what the state is to normalize it so it's a unique value lets just return it
    return newstate

  ########
  # state_changed - handler for state changes
  ########
  def state_change(self,trigger,attributes,old,new,kwargs):
    self.log("trigger={} old = {}-{} new= {}-{}".format(trigger,old,self.convert_dev_state(old),new,self.convert_dev_state(new)))
    if not ((self.convert_dev_state(old)==self.convert_dev_state(new)) or (new=="unavailable")):     # control entity changed state
      for target in self.control_dict[trigger]:            # loop through lights controled by control entity
        self.set_light_state(trigger,target,new)

  ########
  #
  # set_light_state - this is the meet of the application
  # decide what to do with a given trigger, light combination
  ########
  def set_light_state(self,trigger,target,trigger_state):
    trigger_type,trigger_name=self.split_entity(trigger)
    trigger_target=self.control_dict[trigger][target]
    target_type,target_name=self.split_entity(target)
    new_target_state=self.control_dict[trigger][target][self.convert_dev_state(trigger_state)]
    self.log("light {}, self.control_dict[trigger][target] {}, trigger_state {} - {}".format(target,trigger_target,trigger_state,self.convert_dev_state(trigger_state)))
    if new_target_state in self.states["off"]:         # if new desired state is off
      self.log("off - New desired state is {}".format(new_target_state))
      self.turn_off(target)
    elif new_target_state.find("delay")>=0:
      ctlstr=new_target_state                          # parse delay string ("delay",state,seconds)
      tmpstr=ctlstr[ctlstr.find(",")+1:]
      onoff=tmpstr[0:tmpstr.find(",")]
      seconds=tmpstr[tmpstr.find(",")+1:]
      self.log("delay - turning {} {} in {} seconds trigger={}  trigger_state={}".format(onoff,target,seconds,trigger,trigger_state))
      self.run_in(self.timer_handler,seconds,target_entity=target,target_state=onoff,trigger=trigger,trigger_state=trigger_state)
    elif new_target_state=="ignore":
      self.log("ignore - do not do anything")
    elif new_target_state=="last":       # new desired state is on or last
      self.log("last - current state={}".format(self.get_state(target,attribute="state")))
      if self.get_state(target,attribute="state") in self.states["on"]:                             # if current state is on
        if target_type=="light"                                        :                                     # is this a light (lights are dimable and have a last_brightness attribute)
          if not self.control_dict[trigger][target]["last_brightness"]=="":                                # is there a value for last brightness
            self.log("last - returning {} to previous state brightness {}".format(target,self.control_dict[trigger][target]["last_brightness"]))
            self.turn_on(target,brightness=self.control_dict[trigger][target]["last_brightness"])              # yes and the light was on so adjust the brightness
            self.control_dict[trigger][target]["last_brightness"]=""                                          # clear last brightness we are done with it
          else:                                                                                          # there wasn't a value for last brightness
            self.log("last - no previous light level must have been off")
            self.turn_off(target)                                                                            # turn light off
        else:                                                                                         # light is  a switch 
          self.log("last - errro - switch so last makes no sense")
          self.turn_off(target)                                                                           # turn if off
      else:                                                                                        # current state is off and desired state is off
        self.log("last - target is off leave it that way")                                                   # light wasn't on in the first place so don't do anything
    #elif new_target_state=="dim":                                                                  # if the new state = dim  - this is to handle dimming lights over time
      #self.log("dim - dim light {} till it's off".format(target))
      #if self.get_state(target,attribute="state") in self.states["on"]:                            # check if the light is on
        #self.run_in(self.dim_light,60,light=target)                                                  # schedule a call back to dim the light some
    else:                                                                                       # else only other option is the desired state = on
      self.log("on - New desired state for {} is {}".format(target,new_target_state))
      self.log("on - {} current state is {}".format(target,self.get_state(target,attribute="state")))
      if self.get_state(target,attribute="state") in self.states["on"]:                            # if the current state is on and desired state is on
        self.log("on - {}'s current state is on".format(target))                                          # light is already on
        if target_type=="light":                                                                      # if light is a dimmer
          self.log("on - {} is a currently on light with brightness set to {} ".format(target,new_target_state))
          self.control_dict[trigger][target]["last_brightness"]=self.get_state(target,attribute="brightness") # save the current brightness
          if new_target_state == "on":                                                                  # if new state = on  
            self.turn_on(target)                                                                          # turn on light 
          else:                                                                                        # value given to dim to, so dim to that value
            self.turn_on(target,brightness=new_target_state)                                              # turn on the light at the given brightness
        else:                                                                                       # else we are not a dimmer
          self.log("on - {} is a currently on switch".format(target))
          self.turn_on(target)                                                                       # light is a switch so just turn it on even though it is on already
      else:                                                                                       # light is off but desired state is on
        if trigger_type in self.direct_light_control:                                               # is the trigger controlling itself like a wall switch, xor door hinge controlling a light
          if target_type=="light":                                                                     # if light is a dimmer
            self.log("on - {} is a currently off light".format(target))                                      
            self.turn_on(target,brightness=new_target_state)                                             # light is currently off so just turn it on at designated brightness
          else:                                                                                        # else light is not a dimmer
            self.log("on - {} is a currently off switch".format(target))
            self.turn_on(target)                                                                         # light is currently off, so just turn it on
        else:
          self.log("on - not sure why this is here - Trigger {} turned on, but light {} is off so leaving it off".format(trigger,target))
    self.log("the end of set_light_state")

#  def dim_light(self,kwargs):
#    light=kwargs.get("light",None)
#    self.log("dimming light={}".format(light))
#    if self.get_state(light) in self.states["on"]:
#      devtypes=["light","switch"]
#      spot_lights=self.build_entity_list("group.app_spotcontrol_spots_lights",devtypes)
#      if not ((self.get_state("input_boolean.spot") in self.states["on"]) and (light in spot_lights)):   # are we dealing with an exception (spot cleaning)
#        current_brightness=self.get_state(light,"brightness")
#        if current_brightness>=self.dim_rate:                                         # not an exception, is the light still bright enough to see
#          self.turn_on(light,brightness= current_brightness-self.dim_rate) # yes, so dim it somemore
#          self.log("new brightness={}".format(self.get_state(light,"brightness")))
#          self.run_in(self.dim_light,300,light=light)                                      # schedule to run again
#        else:
#          self.turn_off(light)                                                            # to dim to see so turn it off
#      else:                                                                               # else this is an exception (spot cleaning)
#        self.log("exception spot is cleaning")
#        self.turn_on(light,brightness=255)
#        self.log("returning to full brightness")
#        self.run_in(self.dim_light,600,light=light)                                       # check again in 10 minutes to start diming again if spot is #done
#    else:
#      self.log("light is finally off don't schedule anymore checks")
    
