"""
=================Licensing===================
<swirl.py> is prepared by Dr. Kai Zhang at KTH, 21/02/2022

<swirl.py> is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
Commercial use of this script is prohibited.

<CONTACT> kaizhang@kth.se for commercial use.

You should have received a copy of the license along with this
work. If not, see <http://creativecommons.org/licenses/by-nc-sa/4.0/>.

=================Usage=======================
Before running the script, make sure the thermo.rho obj is written in OF.

Ideally, mean values should be used, but it is often the case the rhoMean is not exported.

In case rho does not exist, try (OF6):
>> <solver> -postProcess -func 'writeObjects(rho)' -time <time>

To run the script, open paraview at case root
Select View->Python Shell->Run script->Choose Swirl.py

A spreadsheet.csv will be written at case root containing numerator and denomenator.

Swirl no = numerator/denomenator/radius is reported in the python shell.

=============================================
"""

##Initialization##
import os
pwr = os.getcwd() + '/'

foam_name = '1.foam' #foam name to load data.
csv_name  = "spreadsheet.csv" # save spreadsheat name
var       = ['rho', 'U', 'pd'] # variables used to calculate swirl no.
origin    = [0.0181, 0.0, 0.0]  # origin of surface
normal    = [1.0, 0.0, 0.0]     # normal direction of surface
static_p  = 101325 #equals to fluid static pressure
radius    = 0.0123 #radius of cut surface
##################

from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()
a1foam = OpenFOAMReader(registrationName=foam_name, FileName=pwr+foam_name)
a1foam.MeshRegions = ['internalMesh']
a1foam.CellArrays = var
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()
animationScene1.GoToLast()
renderView1 = GetActiveViewOrCreate('RenderView')
renderView1.Update()
slice1 = Slice(registrationName='Slice1', Input=a1foam)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]
slice1.SliceType.Origin = origin
slice1.SliceType.Normal = normal
renderView1.Update()
calculator1 = Calculator(registrationName='Calculator1', Input=slice1)
calculator1.Function = ''
calculator1.ResultArrayName = 'radialUnit'
calculator1.Function = '(coords-{}*iHat+{}*jHat+{}*kHat)/mag(coords-{}*iHat+{}*jHat+{}*kHat)'.format(origin[0], origin[1], origin[2],origin[0], origin[1], origin[2])
calculator2 = Calculator(registrationName='Calculator2', Input=calculator1)
calculator2.Function = ''
calculator2.ResultArrayName = 'tangentUnit'
calculator2.Function = 'cross(radialUnit, ({}*iHat+{}*jHat+{}*kHat))'.format(normal[0], normal[1], normal[2])
calculator3 = Calculator(registrationName='Calculator3', Input=calculator2)
calculator3.Function = ''
calculator3.ResultArrayName = 'magTangentialU'
calculator3.Function = 'mag((U.radialUnit)*radialUnit+(U.tangentUnit)*tangentUnit)'
calculator4 = Calculator(registrationName='Calculator4', Input=calculator3)
calculator4.Function = ''
calculator4.ResultArrayName = 'numerator'
calculator4.Function = '(rho*U_X*magTangentialU) * (mag((coords-({}*iHat+{}*jHat+{}*kHat))))^2'.format(origin[0], origin[1], origin[2])
calculator5 = Calculator(registrationName='Calculator5', Input=calculator4)
calculator5.Function = ''
calculator5.ResultArrayName = 'denomenator'
calculator5.Function = '(rho*U_X^2 + (pd-{})) * mag((coords-({}*iHat+{}*jHat+{}*kHat)))'.format(static_p, origin[0], origin[1], origin[2])
integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=calculator5)
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.BlockSize = 1024
integrateVariables1Display = Show(integrateVariables1, spreadSheetView1, 'SpreadSheetRepresentation')
layout1 = GetLayoutByName("Layout #1")
AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=0)
spreadSheetView1.HiddenColumnLabels = var
paraview.simple._DisableFirstRenderCameraReset()
spreadSheetView2 = GetActiveViewOrCreate('SpreadSheetView')
ExportView(pwr+csv_name, view=spreadSheetView2)
import pandas as pd
data = pd.read_csv(pwr+csv_name)
print ("swirl no = {}".format(data["numerator"].values/data["denomenator"].values/radius))
