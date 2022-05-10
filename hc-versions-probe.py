#!/usr/bin/env python3
#
## hc-versions-probe.sh
## 2022-04-26 ml4
## Automate the outputting of useful information about HashiCorp products.
## NOTE: this software is provided AS-IS. No warrantee exists with this software.  Read and understand the code
## prior to running, and run in non-production prior to then running in production.
#
#######################################################################################################################

import argparse
import os
import requests
import json
import re

############################################################################
#
#   Globals
#
############################################################################

QUIET = False
norows, columns = os.popen('stty size', 'r').read().split()

############################################################################
#
# Class: bcolors
#
############################################################################

## bcolors - used to provide more engaging output
#
class bcolors:
  Red      = '\033[0;31m'
  Green    = '\033[0;32m'
  Blue     = '\033[0;34m'
  Cyan     = '\033[0;36m'
  White    = '\033[0;37m'
  Yellow   = '\033[0;33m'
  Magenta  = '\033[0;35m'
  BRed     = '\033[1;31m'
  BGreen   = '\033[1;32m'
  BBlue    = '\033[1;34m'
  BCyan    = '\033[1;36m'
  BWhite   = '\033[1;37m'
  BYellow  = '\033[1;33m'
  BMagenta = '\033[1;35m'
  Grey     = '\033[90m'
  Default  = '\033[1;32m'
  Endc     = '\033[0m'
#
## End Class bcolors

############################################################################
#
# def getKeysByStringPartValue
#
############################################################################

## https://thispointer.com/python-how-to-find-keys-by-value-in-dictionary/
## Get a list of keys from dictionary which has the given value
#
def getKeysByStringPartValue(dictOfElements, valueToFind):
  listOfKeys = list()
  listOfItems = dictOfElements.items()
  for item in listOfItems:
      type(item)
      # for subStr in item[1].split()
      #     if subStr == valueToFind:
      #         listOfKeys.append(item[0])

  return listOfKeys
#
## End Func getKeysByStringPartValue

############################################################################
#
# def line
#
############################################################################

## output a line the width of the terminal
#
def line():
  line = '#' * int(columns)
  print(line)

############################################################################
#
# def callVersionsAPI
#
############################################################################

## call vault and return json object
#
def callVersionsAPI(QUIET, path):
  if not path:
    print(f'{bcolors.BRed}No API in calling path{bcolors.Endc}')
    exit(1)

  r = requests.get(f'https://api.releases.hashicorp.com/v1{path}', allow_redirects=True)
  json = r.json()
  return(json)
#
## End Func callVersionsAPI

############################################################################
#
# def outputToolInfo
#
############################################################################

## output tool info
#
def outputToolInfo(QUIET, tool, ent, latest):
  tfNote = False
  latestSP = ''
  if not QUIET:
    line()
    print(f'{bcolors.Default}HashiCorp Tool Information: {bcolors.BWhite}{tool}{bcolors.Endc}')


  ## products
  #
  products = callVersionsAPI(QUIET, f'/products')
  numProducts = 0
  numTFProviders = 0
  for product in products:
    numProducts += 1
    if 'terraform-provider' in product:
      numTFProviders += 1

  if not QUIET:
    print(f'{bcolors.Green}{bcolors.Default}Total products:             {bcolors.BWhite}{numProducts}{bcolors.Endc}')
    line()
    print()

  if ent:
    print(f'{bcolors.Cyan}Shows latest enterprise versions only, not betas, or release candidates.{bcolors.Endc}')

  if latest:
    print(f'{bcolors.Cyan}Shows latest version available.{bcolors.Endc}')

  if tool == 'all' and ent is False:
    tools = ['boundary', 'consul', 'nomad', 'packer', 'terraform', 'vagrant', 'vault', 'waypoint']
  elif tool == 'all' and ent is True:
    tools = ['consul', 'nomad', 'vault']
    tfNote = True
  else:
    tools = [f'{tool}']

  print()
  for mainProduct in tools:
    mainData = callVersionsAPI(QUIET, f'/releases/{mainProduct}')
    for main in mainData:
      v = main["version"]
      if latest:
        break
      else:
        latestSP = 'Stable'
      if re.search('-rc.*', v) or re.search('-beta.*', v):
        next
      if ent:
        if re.search('\d+\.\d+\.\d\+ent$', v):
          break
      elif re.search('\d+\.\d+\.\d+$', v):
        break

    if mainProduct == 'boundary':
      print(f'{bcolors.BRed}boundary.{bcolors.Default}Latest{latestSP}:  {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
    if mainProduct == 'consul':
      print(f'{bcolors.BMagenta}consul.{bcolors.Default}Latest{latestSP}:    {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
    if mainProduct == 'nomad':
      print(f'{bcolors.BGreen}nomad.{bcolors.Default}Latest{latestSP}:     {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
    if mainProduct == 'packer':
      print(f'{bcolors.BCyan}packer.{bcolors.Default}Latest{latestSP}:    {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
    if mainProduct == 'terraform':
      print(f'{bcolors.Magenta}terraform.{bcolors.Default}Latest{latestSP}: {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
      if tool == 'terraform':
        print(f'{bcolors.Green}terraformProvider.{bcolors.Default}Number: {bcolors.BWhite}{numTFProviders}{bcolors.Endc}')
    if mainProduct == 'vagrant':
      print(f'{bcolors.BBlue}vagrant.{bcolors.Default}Latest{latestSP}:   {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
    if mainProduct == 'vault':
      print(f'{bcolors.BYellow}vault.{bcolors.Default}Latest{latestSP}:     {bcolors.BWhite}{main["version"]}{bcolors.Endc}')
    if mainProduct == 'waypoint':
      print(f'{bcolors.Cyan}waypoint.{bcolors.Default}Latest{latestSP}:  {bcolors.BWhite}{main["version"]}{bcolors.Endc}')

  if tfNote:
    print()
    print(f'{bcolors.Magenta}NOTE: {bcolors.Default}Terraform Enterprise versions are not hosted on releases{bcolors.Endc}')

  if not QUIET:
    print()
#
## End Func handler

############################################################################
#
# def MAIN
#
############################################################################

#    #   ##   # #    #
##  ##  #  #  # ##   #
# ## # #    # # # #  #
#    # ###### # #  # #
#    # #    # # #   ##
#    # #    # # #    #

## Main
#
def main():
    ## create parser
    #
    parser = argparse.ArgumentParser(
        description=f'HashiCorp version probe, for convenient iteration of tooling for rudimentary reporting, filtering release candidates and betas by default.',
        formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=80, width=130)
    )
    optional = parser._action_groups.pop()

    system    = parser.add_argument_group('To just output information about the system as a whole')
    quiet     = parser.add_argument_group('Hide dressing for better pipeline work')

    ## add arguments to the parser
    #
    system.add_argument('-t', '--tool', type=str, help='Output information about a specific tool')
    system.add_argument('-e', '--ent',           action='store_true', help='Just show enterprise versions')
    system.add_argument('-l', '--latest',        action='store_true', help='Show the absolute latest')
    quiet.add_argument('-q', '--quiet',          action='store_true', help='Hide extraneous output')

    parser._action_groups.append(optional)

    ## parse
    #
    arg = parser.parse_args()

    if arg.quiet:
      QUIET = True
    else:
      QUIET = False

    if arg.tool:
      tool = arg.tool
    else:
      tool = 'all'

    if arg.latest:
      latest = True
    else:
      latest = False

    if arg.ent:
      ent = True
      if tool == 'boundary' or tool == 'packer' or tool == 'vagrant' or tool == 'waypoint' or tool == 'terraform':
        print(f'{bcolors.BYellow}Specify an enterprise tool{bcolors.Endc}')
        if tool == 'terraform':
          print(f'{bcolors.Magenta}TFE versions are not referred in this API yet.{bcolors.Endc}')
        exit(1)
    else:
      ent = False

    if ent and latest:
      print(f'{bcolors.BRed}Specify -e or -l, not both{bcolors.Endc}')
      exit(1)

    outputToolInfo(QUIET, tool, ent, latest)

if __name__ == '__main__':
    main()

