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
#    return 0
    #self.log("type={} name={}".format(test.get_type(),test.get_name()))
    #test.turn_off()
    self.dim_rate=50
    self.house_map=["HOME","HOUSE"]
    self.dow_map=["M","T","W","TH","F","S","SU"]
    self.states={"on":["on","open","23","playing","Home","home","house","above_horizon"],
                 "off":["off","closed","22",0,"0",
                        "not_home","Academy","Bayer","Corporate",                # handle non-home zones
                        "covington pike","frayser","Macon Rd","MBA",             # non-home zones
                        "Quince","Southaven","Spottswood","UOM",                # non-home zones
                        "Winchester",                                            # non-home zones
                        "None","below_horizon"]}
    # Control_dict structure
    #"trigger":{ "target" : { "On_Trigger_state": "target_state", "Off_Trigger_State": "target_state"},
    #          { "target" : { "on"              : "on"          , "off"              : "off"}}

    self.control_dict={"switch.breakfast_room_light":{"switch.breakfast_room_light":{"on":"on","off":"off"}},
                       #"light.office_lights":{"light.office_lights":{"on":"50","off":"0","last_brightness":""}},
                       #"light.office_fan":{"light.office_fan":{"on":"128","off":"0","last_brightness":""}},
                       #"sensor.ge_32563_hinge_pin_smart_door_sensor_access_control_4_9":{"light.office_lights":{"on":"50","off":"0","last_brightness":""}},
                       #"media_player.dentv":{"light.den_fan_light":{"on":"10","off":"last","last_brightness":""},
                       #                      "switch.breakfast_room_light":{"on":"off","off":"on"}},
                       #"media_player.office_directv":{"light.office_lights":{"on":"10","off":"last","last_brigthness":""}},
                       "switch.downstairs_hallway_light":{"switch.downstairs_hallway_light":{"on":"on","off":"off"}},
                       "switch.carriage_lights":{"switch.carriage_lights":{"on":"on","off":"off"}},
                       "sun.sun":{"switch.carriage_lights":{"on":"off","off":"on"},
                                  "switch.back_porch_light":{"on":"off","off":"on"}},
                       "light.master_light_switch":{"light.master_light_switch":{"on":"255","off":"0","last_brightness":""}},
                       "light.shed_lights":{"light.shed_lights":{"on":"255","off":"0","last_brightness":""}},
                       "light.shed_flood_light":{"light.shed_flood_light":{"on":"255","off":"0","last_brightness":""}},
                       "light.upstairs_hallway_lights":{"light.upstairs_hallway_lights":{"on":"255","off":"0","last_brightness":""}},
                       "switch.pulldown_attic":{"switch.pulldown_attic":{"on":"delay,off,3600","off":"off"}},
                       #"device_tracker.scox0129_sc0129":{"switch.downstairs_hallway_light":{"on":"on","off":"ignore"},
                       #                                  "light.sam_light_switch":{"on":"ignore","off":"0","last_brightness":""},
                       #                                  "light.sam_fan_switch":{"on":"ignore","off":"0","last_brightness":""},
                       #                                  "switch.sam_toilet_fan":{"on":"ignore","off":"0"},
                       #                                  "switch.sam_toilet_light":{"on":"ignore","off":"0"},
                       #                                  "switch.sam_vanity_switch":{"on":"ignore","off":"0"}},
                       #"light.sam_light_switch":{"light.sam_light_switch":{"on":"255","off":"0","last_brightness":""}},
                       #"light.sam_fan_switch":{"light.sam_fan_switch":{"on":"128","off":"0","last_brightness":""}},
                       "device_tracker.ccox0605_ccox0605":{"switch.downstairs_hallway_light":{"on":"on","off":"ignore"},
                                                           "light.charlie_light_switch":{"on":"ignore","off":"0","last_brightness":""},
                                                           "light.charlie_fan_switch":{"on":"255","off":"126","last_brightness":""}},
                       "light.charlie_light_switch":{"light.charlie_light_switch":{"on":"255","off":"0","last_brightness":""}},
                       "light.charlie_fan_switch":{"light.charlie_fan_switch":{"on":"128","off":"0","last_brightness":""}},
                       "switch.media_room_lights":{"switch.media_room_lights":{"on":"on","off":"off"}},
                       "light.media_room_fan":{"light.media_room_fan":{"on":"128","off":"0","last_brightness":""}},
                       "input_boolean.masterishome":{"light.master_light_switch":{"on":"ignore","off":"0","last_brightness":""},
                                                         "light.master_fan":{"on":"ignore","off":"0","last_brightness":""},
                                                         "light.master_floor_light":{"on":"ignore","off":"0","last_brightness":""},
                                                         "switch.master_toilet_fan":{"on":"ignore","off":"0"},
                                                         "switch.master_toilet_light":{"on":"ignore","off":"0"},
                                                         "switch.downstairs_hallway_light":{"on":"on","off":"off"}},
                       "device_tracker.scox1209_scox1209":{"input_boolean.masterishome":{"on":"on","off":"dtupdate,group.app_light_control_master"}},
                       "device_tracker.turboc1208_cc1208":{"input_boolean.masterishome":{"on":"on","off":"dtupdate,group.app_light_control_master"}},
                       "input_boolean.master_bath_high_humidity":{"switch.master_bath_fan":{"on":"on","off":"off"}},
                       "light.master_floor_light":{"light.master_floor_light":{"on":"128","off":"0","last_brightness":""}},
                       "switch.master_toilet_light":{"switch.master_toilet_fan":{"on":"delay,on,300","off":"delay,off,300"}},
                       "switch.half_bath_light":{"switch.half_bath_fan":{"on":"delay,on,300","off":"delay,off,300"}},
                       #"switch.sam_toilet_light":{"switch.sam_toilet_fan":{"on":"delay,on,300","off":"delay,off,300"}},
                       "time":{"19:00:00":{"light.front_porch_lights":{"state":"on","dow":"m,t,w,th,f"}},
                               "23:30:00":{"switch.back__porch_light":{"state":"off","dow":"all"}}},
                       "binary_sensor.ring_front_door_ding":{"switch.front_door_light":{"on":"on","off":"delay,off,900"}} }

    self.exception_dict={"light.sam_light_switch":["input_boolean.samishomeoverride"],
                         "light.sam_toilet_light":["input_boolean.samishomeoverride","input_boolean.guestishomeoverride"],
                         "light.sam_vanity_switch":["input_boolean.samishomeoverride","input_boolean.guestishomeoverride"],
                         "light.charlie_light_switch":["input_boolean.charlieishomeoverride"],
                         "light.master_floor_light":["input_boolean.masterishomeoverride"],
                         "light.master_light_switch":["input_boolean.masterishomeoverride"],
                         "light.office_lights":["input_boolean.partyoverride"],
                         "light.shed_flood_light":["input_boolean.partyoverride"],
                         "light.stairway_light_switch":["input_boolean.partyoverride","input_boolean.samishomeoverride",
                                                        "input_boolean.charlieishomeoverride","input_boolean.guestishomeoverride"],
                         "light.den_fan_light":["input_boolean.partyoverride","input_boolean.samishomeoverride",
                                                "input_boolean.charlieishomeoverride","input_boolean.guestishomeoverride"],
                         "switch.back_porch_light":["input_boolean.partyoverride"],
                         "switch.breakfast_room_light":["input_boolean.partyoverride"],
                         "switch.downstairs_hallway_light":["input_boolean.partyoverride","input_boolean.samishomeoverride",
                                                         "input_boolean.charlieishomeoverride","input_boolean.guestishomeoverride"],
                         "switch.front_door_light":["input_boolean.partyoverride"],
                         "switch.garage_lights":["input_boolean.partyoverride"],
                         "switch.guest_light_switch":["input_boolean.partyoverride","input_boolean.guestishomeoverride"],
                         "switch.half_bath_light":["input_boolean.partyoverride"],
                         "switch.house_flood_lights":["input_boolean.partyoverride"],
                         "switch.media_room_lights":["input_boolean.partyoverride"]}

    #self.log("group.app_light_control_master = {}".format(self.get_state("group.app_light_control_master")))

    self.direct_light_control=["switch","light","sensor","binary_sensor","input_boolean","device_tracker","group","sun"]

    for trigger in self.control_dict:
      if trigger=="time":
        for runtime in self.control_dict[trigger]:
          for target_entity in self.control_dict[trigger][runtime]:
            self.log("scheduling {} to turn {} at {} on {} days".format(target_entity,self.control_dict[trigger][runtime][target_entity]["state"],
                                                                        runtime,self.control_dict[trigger][runtime][target_entity]["dow"]))
            self.run_daily(self.timer_handler,self.parse_time(runtime),target_entity=target_entity,target_state=self.control_dict[trigger][runtime][target_entity]["state"],
                                                                       dow=self.control_dict[trigger][runtime][target_entity]["dow"])
      else:
        self.log("listening for {}".format(trigger))
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
    if ((self.convert_dev_state(old)!=self.convert_dev_state(new)) and (new!="unavailable")):     # control entity changed state
      for target in self.control_dict[trigger]:            # loop through lights controled by control entity
        self.log("checking on target={}-{}".format(target, self.control_dict[trigger][target]))
        self.set_light_state(trigger,target,new)

  def update_location(self,tracker,referenceentity):
   self.log("in update_location")
   tracker_list=[]
   trackerishome=False
   tracker_type,tracker_name=self.split_entity(tracker)
   if tracker_type=="group":
     tracker_list=self.build_entity_list(tracker) 
   else:
     tracker_list.append(tracker)
   self.log("tracker_list={}".format(tracker_list))
   for t in tracker_list:
     self.log("checking on {}".format(t))
     self.log("t={} state={}".format(t,self.get_state(t).upper()))
     if self.get_state(t).upper() in self.house_map:
       self.log("{} is home".format(t))
       trackerishome=True

   if trackerishome:
     self.turn_on(referenceentity)
   else:
     self.turn_off(referenceentity)

  ########
  #
  # set_light_state - this is the meet of the application
  # decide what to do with a given trigger, light combination
  ########
  def set_light_state(self,trigger,target,trigger_state):
    trigger_type,trigger_name=self.split_entity(trigger)
    trigger_target=self.control_dict[trigger][target]
    target_type,target_name=self.split_entity(target)
    if callable(self.control_dict[trigger][target]):
      self.log("preparing to execute {}".format(self.control_dict[trigger][target]))
      self.control_dict[trigger][target](trigger,target)
    else:
      new_target_state=self.control_dict[trigger][target][self.convert_dev_state(trigger_state)]
      self.log("light {}, self.control_dict[trigger][target] {}, trigger_state {} - {}".format(target,trigger_target,trigger_state,self.convert_dev_state(trigger_state)))
      self.log("new_target_state={}".format(new_target_state))
      if new_target_state in self.states["off"]:         # if new desired state is off
        self.log("off - New desired state is {}".format(new_target_state))
        self.turn_off(target)
      elif new_target_state.find("dtupdate")>=0:
        ctlstr=new_target_state
        tstentity=new_target_state[new_target_state.find(",")+1:]
        self.update_location(tstentity,target)
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

  def calc_humidity(self,trigger,target):
    self.log("trigger={},target={}".format(trigger,target))
    if int(self.get_state(trigger))>78:
      self.turn_on(target)
    else:
      self.turn_off(target)

  def turn_off(self,entity_id):
    self.log("in local turn_off {}".format(entity_id))
    exception=False
    if entity_id in self.exception_dict:
      for override in self.exception_dict[entity_id]:
        self.log("is {} in {} - {}".format(entity_id,override,self.get_state(override)))
        if self.get_state(override)=="on":
          self.log("exception do not turn off light")
          exception=True
    
    if not exception:
      super().turn_off(entity_id)      
    
