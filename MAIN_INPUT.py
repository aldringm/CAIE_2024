import pandas as pd
#from CONTROLLER_SIM import controlador
from CONTROLLER_SIM2 import controlador

#FILE PATH
file_path = "F:\Simulador_Mina\Input" # PATH OF THE INPUT FILES
output_path =  "F:\Simulador_Mina\Output" #PATH OF OUTPUT FILES

#SIMULATION SET
v_prioritization = "size" # HIGHEST PRIORITIZATION TARGET. "size" = PARTICLE SIZE, "grade" = ELEMENT GRADE, "same" = PARTICLE SIZE TARGET PRIORITIZATION IS EQUAL TO ELEMENT GRADE PRIORITIZATION
v_rem = 0.78 # STRIPPING RATIO TARGET
v_optimization_time = 6 # OPTIMIZATION TIME OR SHIFT DURATION IN HOURS
v_simulation_time= 365 # NUMBER OF SIMULATION DAYS
v_tolerance = 0 # TOLERANCE FOR THE ELEMENT GRADE TARGET
m_v_num_rep = 1 # INITIALIZES THE NUMBER OF REPLICATIONS
m_v_start_rep = 1 # INITIALIZES THE REPLICATION INDEX

# TRUCK DATA
df_Truck= pd.read_csv(file_path + '\Input_Truck.csv')  # IT IMPORTS TRUCK FLEET DATA
df_Truck.set_index('ID', drop=False, inplace=True)
df_MainBetTime_truck = pd.read_csv(file_path + '\Input_MaintBetweenTime_Truck.csv') #IT IMPORTS THE TIME BETWEEN MAINTENANCE OF THE TRUCKS
df_MainBetTime_truck.set_index('ID', drop=False, inplace=True)
df_MainDurTime_truck = pd.read_csv(file_path + '\Input_MaintDurationTime_Truck.csv') #IT IMPORTS THE DURATION TIME OF THE TRUCK MAINTENANCE
df_MainDurTime_truck.set_index('ID', drop=False, inplace=True)
df_EmpHaulage_truck = pd.read_csv(file_path + '\Input_EmptyTime.csv') # IT IMPORTS THE EMPTY HAULAGE TIME
df_LoadHaulage_truck = pd.read_csv(file_path + '\Input_LoadedTime.csv') # IT IMPORTS THE LOADED HAULAGE TIME
df_LoadTime_truck = pd.read_csv(file_path + '\Input_LoadingTime.csv') # IT IMPORTS THE LOADING TIME OF THE TRUCKS
df_UnloaTime_truck = pd.read_csv(file_path + '\Input_UnloadingTime.csv') #IT IMPORTS THE UNLOADING TIME OF THE TRUCKS

#LOADING MACHINE DATA
df_LoadingMachine = pd.read_csv(file_path + '\Input_LoaderMachine.csv') # IT IMPORTS THE LOADING MACHINE DATA
df_LoadingMachine.set_index('ID', drop=False, inplace=True)
df_MainBetTime_loader = pd.read_csv(file_path + '\Input_MaintBetweenTime_Loader.csv') #IMPORT THE TIME BETWEEN MAINTENANCE OF THE LOADING MACHINES
df_MainBetTime_loader.set_index("ID", drop=False, inplace=True)
df_MainDurTime_loader = pd.read_csv(file_path + '\Input_MaintDurationTime_Loader.csv') #IT IMPORTS THE DURATION TIME OF THE LOADING MACHINE MAINTENANCE
df_MainDurTime_loader.set_index("ID", drop=False, inplace=True)
df_LocalComp = pd.read_csv(file_path + '\Input_LocalComp.csv') #COMPATIBILITIES BETWEEN MINE REGIONS AND LOADING MACHINES
df_LocalComp.set_index("ID", drop=False, inplace=True)
df_MovTime_loader = pd.read_csv(file_path + '\Input_MovTime.csv') #IT IMPORTS THE MOVEMENT TIMES OF THE LOADING MACHINES BETEWEEN THE REGIONS
df_MovTime_loader.set_index("ID", drop=False, inplace=True)

#DISCHARGE DATA
df_Discharge = pd.read_csv(file_path + '\Input_Discharge.csv') # IT IMPORTS THE DISCHARGE DATA
df_Discharge.set_index("ID",drop = False, inplace = True)
df_Discharge.insert(9, "Massa", [0,0,0,0])

#ORE PROCESSING PLANT DATA
df_Plant = pd.read_csv(file_path + '\Input_OrePlant.csv') # IT IMPORTS ORE PLANT DATA
df_Plant.set_index('ID', drop=False, inplace=True)
df_MainBetTime_plant = pd.read_csv(file_path + '\Input_MaintBetweenTime_OrePlant.csv') #IT IMPORTS THE TIME BETWEEN MAINTENANCE OF THE ORE PLANTS
df_MainBetTime_plant.set_index('ID', drop=False, inplace=True)
df_MainDurTime_plant = pd.read_csv(file_path + '\Input_MaintBetweenTime_OrePlant.csv') #IT IMPORTS THE DURATION TIME OF THE ORE PLANT MAINTENANCE
df_MainDurTime_plant.set_index('ID', drop=False, inplace=True)

# OTHER ACTIVITIES DATA
df_ShiftTurn = pd.read_csv(file_path + '\Input_ShiftTurn.csv') #IT IMPORTS THE SHIFT CHANGE TIME WINDOW
df_ShiftTurn.set_index("ID", drop=False, inplace=True)
df_ShiftTurn["Inicio"] = pd.to_numeric(df_ShiftTurn["Inicio"], downcast="float") #IT IMPORTS THE DURATION TIME OF THE SHIFT CHANGE
df_ShiftTurn["Fim"] = pd.to_numeric(df_ShiftTurn["Fim"], downcast="float")
df_Refueling = pd.read_csv(file_path + '\Input_Refueling.csv') #IT IMPORTS THE SHIFT CHANGE TIME WINDOW.
df_Refueling.set_index("ID", drop=False, inplace=True)
df_Refueling["Autonomia"] = pd.to_numeric(df_Refueling["Autonomia"], downcast="float") #IT IMPORT THE FUEL AUTONOMY
df_Refueling["Tempo"] = pd.to_numeric(df_Refueling["Tempo"], downcast="float")
df_Random = pd.read_csv(file_path + '\Input_Random.csv') #IT IMPORTS THE TIME BETWEEN RANDOM EVENTS.
df_Random.set_index("ID", drop=False, inplace=True)
df_RandDurTime = pd.read_csv(file_path + '\Input_DurationTimeRandom.csv') #IT IMPORTS THE DURATION TIME OF THE RANDOM EVENTS.
df_RandDurTime.set_index("ID", drop=False, inplace=True)

l_Materials = ["1","2","3","4"] #MATERIAL TYPE LIST.

#LIST OF MINE REGION INDEXES.
l_Regions = ['Mina_2#Regiao_1', 'Mina_1#Regiao_3', 'Mina_3#Regiao_1', 'Mina_1#Regiao_6', 'Mina_1#Regiao_4', 'Mina_1#Regiao_1', 'Mina_1#Regiao_5', 'Mina_1#Regiao_2']

d_regions = {}
cont = 0
for i in l_Regions:
    d_regions[i] =  pd.read_csv(file_path + '\\region'+ str(cont) +'.csv')
    d_regions[i]["Tipo"] = d_regions[i]["Tipo"].astype(str)
    cont +=1
v_WasteName = ['1'] #WASTE TYPE.
v_MassName = 'Massa' #NAME OF MASS COLUMN IN DATA REGION DATA.
v_MaterialsName = 'Tipo' #NAME OF LITOLOGY COLUMN IN DATA REGION DATA.
d_LowerBoundGrade= {('BRIT_SECO', 'FET'):57, ('BRIT_PRIM', 'FET'):54, ('BRIT_PRIM', 'P3'):0.065, ('BRIT_PRIM', 'MN3'):0.5} # LOWER BOUND OF THE ELEMENT GRADE TARGETS.
d_UpperBoundGrade= {('BRIT_SECO', 'FET'):57, ('BRIT_PRIM', 'FET'):54, ('BRIT_PRIM', 'P3'):0.065, ('BRIT_PRIM', 'MN3'):0.5} # UPPER BOUND OF THE ELEMENT GRADE TARGETS.
d_LowerBoundSize = {('BRIT_PRIM', 'G1'):24, ('BRIT_PRIM', 'G3'):50} #LOWER BOUND OF THE PARTICLE SIZE TARGETS.
d_UpperBoundSize = {('BRIT_PRIM', 'G1'):24, ('BRIT_PRIM', 'G3'):50} #UPPER BOUND OF THE PARTICLE SIZE TARGETS.

#DICTIONARY OF THE UML MASSES OF EACH MINE REGION.
d_RegionMass = {'Mina_2#Regiao_1': [101433, 1572, 1791, 6110, 16025, 9986, 13300, 2238, 2564, 13091, 11437, 38024, 20580, 27875, 1719, 128984, 8522, 11905, 18304, 52232, 1036, 38580, 12077, 3459, 5881, 43920, 2691, 25019, 16531, 4053, 112950, 58756, 58255, 34406, 4707, 1021, 233407, 41174, 33914, 107423, 38967, 28627, 170, 7576, 6661, 18745, 10111, 24755, 53802, 59303, 5720, 27787, 14503, 131819, 74779, 11668, 81304, 68134, 4936, 27304, 8331, 1358, 5870, 26645, 18161, 39517, 339386, 51706, 103751, 157730, 23735, 35228, 48251, 1867, 2956, 76024, 51886, 6027, 1715, 65275, 47006, 4610, 23073, 33541, 117663, 154623, 2955, 6611, 112499, 7292, 852, 27260, 6362, 4974, 8182, 278678, 75158, 7764, 224043, 373140, 16852, 229771, 89054, 164558, 22900, 67972, 6395, 2671, 1257, 7384, 2711, 4082, 32901, 3620, 40001, 10692, 228084, 15118, 35030, 19109, 2067, 3766, 1136, 2495, 756], 'Mina_1#Regiao_3': [8666, 19835, 1809, 18385, 36437, 46853, 27547, 23490, 45049, 48236, 40330, 45636, 15472, 74173, 2476, 29654, 27214, 47792, 28776, 18534, 44724, 41250, 17017, 5003, 41115, 32302, 18583, 93592, 27344, 19682, 30173, 16540, 5836, 56052, 53528, 101180, 898, 84168, 86048, 282796, 23111, 37068, 2719, 6074, 11482, 10725, 10279, 12263, 84824, 115213, 37414, 176760, 32979, 257916, 12695, 12331, 21551, 20232, 100735, 67938, 107546, 97655, 103676, 173477, 3779, 15887, 7420, 35722, 123558, 33141, 137936, 55118, 230243, 68054, 78055, 16180, 8578, 36259, 288569, 13217, 9532, 317711, 9469, 206505, 16034, 71279], 'Mina_3#Regiao_1': [13495, 9748, 24648, 3699, 403, 45617, 18251, 36980, 6390, 3210, 52857, 75864, 50264, 997, 386, 3730, 1874, 1544, 74503, 81145, 62247, 27404, 76143, 14705, 54612, 146017, 148729, 73031, 50438, 85328, 5363, 11736, 78026, 250277, 350498, 43376, 55842, 6873, 48318, 75109, 183138, 426789, 43643, 45550, 251645, 281576, 47499, 17111, 16691, 274557, 135554, 55769, 1461, 34130, 10735, 87210, 79487, 39011, 12295], 'Mina_1#Regiao_6': [39806, 1530, 40033, 27900, 29180, 14030, 29032, 24111, 32496, 37595, 8213, 35549, 35498, 34946, 49389, 6811, 26042, 44857, 39375, 4721, 31019, 24724, 12387, 48219, 41801, 43179, 6673, 33772, 83463, 124546, 14203, 168858, 17442, 7638, 7483, 24430, 94851, 41286, 31310, 82842, 71521, 77520, 163839, 58600, 1768, 134837, 21165, 263449, 19832, 33583, 222377, 6141, 50184, 72196], 'Mina_1#Regiao_4': [77267, 92555, 10150, 43781, 1255, 22294, 25502, 19983, 70606, 2538, 67117, 74444, 47397, 128607, 32172, 6851, 17494, 33803, 15606, 292, 4531, 53034, 30359, 5265, 130397, 24061, 190316, 20391, 888, 20692, 22203, 4638, 25096, 10875, 1521, 43011, 68449, 134411, 196271, 1273, 888, 126464, 160778, 253, 161578, 4456], 'Mina_1#Regiao_1': [1326, 2477, 10416, 139370, 7120, 8867, 30442, 173956, 58083, 251921, 24488, 294435, 27207, 90095, 465669, 136287, 3189, 23744, 227585, 2440, 79021, 140705, 6194, 609932, 59032, 3039, 49495, 25013, 224639, 1422, 4058, 107762, 111291, 2624, 453539, 21442, 8790, 5395, 219852, 10316, 244817, 122754, 354659], 'Mina_1#Regiao_5': [9279, 58770, 74236, 410004, 182671, 173846, 47035, 333123, 84019, 98728, 59468], 'Mina_1#Regiao_2': [2998, 60093, 15342, 433880, 52344, 91115, 110614, 100041]}

# WEIGHT FACTOR OF EACH ORE PARAMETER.
d_WeightGrades = {'FET': 'Global', 'SIT': 'Global', 'PT': 'Global', 'ALT': 'Global', 'MNT': 'Global', 'PPCT': 'Global', 'FE1': 'G1', 'SI1': 'G1', 'P1': 'G1', 'AL1': 'G1', 'MN1': 'G1', 'PPC1': 'G1', 'FE2': 'G2', 'SI2': 'G2', 'P2': 'G2', 'AL2': 'G2', 'MN2': 'G2', 'PPC2': 'G2', 'FE3': 'G3', 'SI3': 'G3', 'P3': 'G3', 'AL3': 'G3', 'MN3': 'G3', 'PPC3': 'G3', 'G1': 'Global', 'G2': 'Global', 'G3': 'Global'}

#DICTIONARY SPECIFYING THE PREFERENCE OF AN ELEMENT GRADE TARGET SHOULD BE MAXIMIZED OR MINIMIZED.
d_MinMaxGrades = {('BRIT_SECO', 'FET'): ' "Max"', ('BRIT_PRIM', 'FET'): 'Max', ('BRIT_PRIM', 'P3'): 'Min', ('BRIT_PRIM', 'MN3'): 'Min'}

#DICTIONARY SPECIFYING THE PREFERENCE OF A PARTICLE SIZE TARGET SHOULD BE MAXIMIZED OR MINIMIZED.
d_MinMaxSizes = {('BRIT_PRIM', 'G3'): 'Min'}

d_Perfom_plant = pd.DataFrame

controlador(l_Materials, d_regions, d_LowerBoundGrade, d_LowerBoundSize, d_UpperBoundGrade, d_UpperBoundSize, d_RegionMass, d_WeightGrades, \
            df_Truck, df_Discharge, df_LoadingMachine, l_Regions, v_WasteName, v_MaterialsName, v_MassName, v_optimization_time, \
            v_simulation_time*1440, v_rem, df_Plant, d_Perfom_plant, df_LoadTime_truck, df_UnloaTime_truck, df_EmpHaulage_truck, \
            df_LoadHaulage_truck, df_MainBetTime_plant, df_MainDurTime_plant, df_MainBetTime_truck, df_MainDurTime_truck, df_ShiftTurn, \
            df_Refueling, df_MovTime_loader, d_MinMaxGrades, d_MinMaxSizes, df_MainBetTime_loader, df_MainDurTime_loader, \
            df_LocalComp, df_Random, df_RandDurTime, file_path, v_prioritization, v_tolerance, output_path, m_v_num_rep, m_v_start_rep)

