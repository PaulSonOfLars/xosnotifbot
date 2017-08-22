#
# Telegram Bot written in Python for halogenOS
# Copyright (C) 2017  Simao Gomes Viana
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Python imports
import os
import sys
from subprocess import call
from os.path import expanduser

# Library imports
import telegram

# Project imports
from utils import getenviron

def get_id(bot, update):
  update.message.reply_text("ID: %s" % update.message.chat_id)

def runs(bot, update):
  update.message.reply_text("Where u going so fast?!")

_jenkins_address = getenviron("NOLIFER_JENKINS_ADDR", "localhost")
_jenkins_port = int(getenviron("NOLIFER_JENKINS_PORT", "6692"))
_jenkins_user = getenviron("NOLIFER_JENKINS_USER", "xdevs23")
_jenkins_project = getenviron("NOLIFER_JENKINS_PROJECT", "halogenOS")
_jenkins_ssh_key = getenviron("NOLIFER_JENKINS_SSHKEY",
                              "%s/.ssh/id_rsa" % expanduser("~"))
def launch_build(bot, update):
  # Family group or my private chat
  if update.message.chat_id == -1001068076699 or \
     update.message.chat_id == 11814515:
    split_msg = update.message.text[len("/build "):].split()
    final_command = "ssh -l %s -i %s %s -p %i build %s" \
                      % (
                         _jenkins_user,
                         _jenkins_ssh_key,
                         _jenkins_address,
                         _jenkins_port,
                         _jenkins_project
                        )
    human_friendly_description = ""
    if len(split_msg) >= 1:
      target_device = split_msg[0]
      final_command += " -p 'Target_device=%s'" % target_device
      human_friendly_description += "Device: %s\n" % target_device
      is_release = False
      if len(split_msg) >= 2:
        split_msg.remove(target_device)
        if "noclean" in split_msg:
          final_command += " -p 'do_clean=false'"
          split_msg.remove("noclean")
          human_friendly_description += "No clean\n"
        if "noreset" in split_msg:
          final_command += " -p 'do_not_reset=true'"
          split_msg.remove("noreset")
          human_friendly_description += "No git reset\n"
        if "release" in split_msg:
          final_command += " -p " \
                           "'Prepare_for_official_release=true' -p " \
                           "'Do_release=true' -p " \
                           "'Auto_release=true'"
          split_msg.remove("release")
          is_release = True

        build_type = "userdebug"
        if "user" in split_msg:
          build_type = "user"
        elif "eng" in split_msg:
          build_type = "eng"

        if build_type in split_msg:
          split_msg.remove(build_type)
        human_friendly_description += "Build type: %s\n" % build_type

        final_command += " -p 'Build_type=%s'" % build_type

        repopick_list = ""
        module_to_build = ""
        had_repopick = False
        for arg in split_msg:
          if had_repopick: break
          if "repopick" in arg:
            start_repopick_ix = split_msg.index(arg)
            for i in range(start_repopick_ix + 1, len(split_msg) - 1):
              if split_msg[i] != "-t":
                repopick_list += "%s," % split_msg[i]
                if i == len(split_msg) - 1:
                  repopick_list = repopick_list[:-1]
              else:
                if len(repopick_list) > 0:
                  repopick_list = repopick_list[:-1]
                repopick_list += "[[NEWLINE]]-t %s[[NEWLINE]]" \
                                    % split_msg[i + 1]
                if i + 1 == len(split_msg) - 1:
                  repopick_list = repopick_list[:-(len("[[NEWLINE]]"))]
                i += 1
            had_repopick = True
          elif len(module_to_build) == 0:
            module_to_build = arg
          else:
            update.message.reply_text("Could not understand your request. "
                                      "Unrecognized argument %s" % arg)
            return

        if had_repopick:
          final_command += " -p 'repopick_before_build=%s'" % repopick_list
          human_friendly_description += "Stuff to repopick:\n%s\n" \
                                          % repopick_list
        if len(module_to_build) > 0:
          final_command += " -p 'Module_to_build=%s'" % module_to_build
          human_friendly_description += "Module: %s\n" % module_to_build
    else:
      update.message.reply_text("Please specify a device like: /build oneplus2")
      return
    call(final_command.split())
    update.message.reply_text("%s build launched\n\n%s" \
                                % ("Release" if is_release else "Test",
                               human_friendly_description.replace("[[NEWLINE]]", "\n")))

commands = [
  ["id", get_id],
  ["runs", runs],
  ["build", launch_build],
]