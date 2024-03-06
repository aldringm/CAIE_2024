import os
import pandas as pd  # ITS IMPORTS THE PANDAS DATAFRAME LIBRARY
import OPTIMIZER_v1 as otimizador  # IT IMPORTS THE OPTIMIZER MODULE
from SIMULATOR_v1 import SIMULATION  # IT IMPORTS THE SIMULATION ROUTINES
import numpy as np  # IT IMPORTS NUMPY LIBRARY
import matplotlib.pyplot as plt  # IT IMPORTS MATPLOTLIB LIBRARY TO PLOT ALIVE GRAPHICS


# SELECT THE FREE MMUS CANDIDATES TO BE EXTRACTED AT THE CURRENT TIME OF THE SIMULATION
def select_freeMMUS(s_d_regions, s_d_RegionsMasses, s_l_regioes, v_MaterialsName, v_WasteName, v_MassName,
                    MaxMassPerRegion, d_WeightGrades):
    o_l_FreeMMUIndex = [] #LIST OF THE FREE MMU INDEXES
    FreeMMUData = {} #DICIONARY WITH ALL DATA FROM THE FREE MMUS
    NM = {} # NUMBER OF MATERIALS PER MMU
    c_v_minimum_mass = 100 # MINIMUM MASS CONSIDERED IN A MMU. A MASS BELOW THIS VALUE IS CONSIDERED EXAUSTHED
    v_WasteMassAvail = 0  # INITIALIZES THE COUNTER OF ORE AVAILABLE IN THE FREE MMUS
    v_OreMassAvail = 0  # INITIALIZES THE COUNTER OF WASTE AVAILABLE IN THE FREE MMUS
    for i in s_l_regioes:
        mass_count = 0
        # FOR EACH REGION, SELECTS THE FREE MMUS BASED ON THE PRECENDENCE ORDER AND THE MAXIMUM MASS CONSIDERED FREE AT EACH MMU
        for j in range(len(s_d_RegionsMasses[i])):
            if s_d_RegionsMasses[i][j] > c_v_minimum_mass and mass_count < MaxMassPerRegion:
                mass_count += s_d_RegionsMasses[i][j]
                if s_d_regions[i][v_MaterialsName].iloc[j] in v_WasteName:
                    v_WasteMassAvail = v_WasteMassAvail + s_d_regions[i][v_MassName].iloc[j]
                else:
                    v_OreMassAvail = v_OreMassAvail + s_d_regions[i][v_MassName].iloc[j]
                if s_d_regions[i]['MMU_'].iloc[j] not in o_l_FreeMMUIndex:
                    o_l_FreeMMUIndex.append(s_d_regions[i]['MMU_'].iloc[j])
                    NM[s_d_regions[i]['MMU_'].iloc[j]] = 1
                else:
                    NM[s_d_regions[i]['MMU_'].iloc[j]] += 1
                FreeMMUData[(s_d_regions[i]['MMU_'].iloc[j], s_d_regions[i][v_MaterialsName].iloc[j])] = s_d_regions[i].iloc[
                    j]
                FreeMMUData[(s_d_regions[i]['MMU_'].iloc[j], s_d_regions[i][v_MaterialsName].iloc[j])]['Posicao'] = j
                FreeMMUData[(s_d_regions[i]['MMU_'].iloc[j], s_d_regions[i][v_MaterialsName].iloc[j])][v_MassName] = \
                    s_d_RegionsMasses[i][j]
        l_aux = []
        l_aux = list(FreeMMUData.keys())
        l_aux1 = []
        if len(l_aux) > 0:
            for k in range(len(l_aux)):
                for j in range(k, len(l_aux)):
                    if k != j and FreeMMUData[l_aux[j]]['Independent_'] == FreeMMUData[l_aux[k]]['Independent_'] and \
                            l_aux[k] not in l_aux1 and l_aux[j] not in l_aux1:

                        if FreeMMUData[l_aux[j]][v_MaterialsName] == FreeMMUData[l_aux[k]][v_MaterialsName] or \
                                (FreeMMUData[l_aux[j]][v_MaterialsName] not in v_WasteName and FreeMMUData[l_aux[k]][
                                    v_MaterialsName] not in v_WasteName and \
                                 FreeMMUData[l_aux[j]]['MMU_'] != FreeMMUData[l_aux[k]]['MMU_']):

                            for l in d_WeightGrades.keys():
                                if d_WeightGrades[l] == "Global":
                                    FreeMMUData[l_aux[k]][l] = (FreeMMUData[l_aux[k]][l] * FreeMMUData[l_aux[k]][v_MassName] + \
                                                           FreeMMUData[l_aux[j]][l] * FreeMMUData[l_aux[j]][v_MassName]) / \
                                                          (FreeMMUData[l_aux[k]][v_MassName] + FreeMMUData[l_aux[j]][
                                                              v_MassName])
                                else:
                                    FreeMMUData[l_aux[k]][l] = (FreeMMUData[l_aux[k]][d_WeightGrades[l]] *
                                                           FreeMMUData[l_aux[k]][l] * FreeMMUData[l_aux[k]][v_MassName] +
                                                           FreeMMUData[l_aux[j]][d_WeightGrades[l]] *
                                                           FreeMMUData[l_aux[j]][l] * FreeMMUData[l_aux[j]][v_MassName]) / \
                                                          (FreeMMUData[l_aux[k]][d_WeightGrades[l]] *
                                                           FreeMMUData[l_aux[k]][v_MassName] + \
                                                           FreeMMUData[l_aux[j]][d_WeightGrades[l]] *
                                                           FreeMMUData[l_aux[j]][v_MassName])
                            FreeMMUData[l_aux[k]][v_MassName] += FreeMMUData[l_aux[j]][v_MassName]
                            s_d_RegionsMasses[FreeMMUData[l_aux[k]]['Independent_']][FreeMMUData[l_aux[k]]['Posicao']] += \
                                FreeMMUData[l_aux[j]][v_MassName]
                            FreeMMUData[l_aux[j]][v_MassName] = 0
                            s_d_RegionsMasses[FreeMMUData[l_aux[j]]['Independent_']][FreeMMUData[l_aux[j]]['Posicao']] = 0
                            l_aux1.append(l_aux[k])
                            l_aux1.append(l_aux[j])

    # CALCULATES THE STRIPPING RATIO OF ALL FREE MMUS
    REM = v_WasteMassAvail / max(v_OreMassAvail, 0.01)

    # RETURN THE DATA OF THE FREES MMUS, THEIR INDEXES, THE NUMBER OF MATERIALS IN EACH MMU, THE STRIPPING RATIO, THE AVAILABLE WASTE AND ORE MATERIAL IN THE FREE MMUS
    return (FreeMMUData, o_l_FreeMMUIndex, NM, REM, v_WasteMassAvail, v_OreMassAvail)


# MAIN FUNCTION CALLED CONTROLLER. THIS FUNCTION MANAGES THE INTERFACE BETWEEN THE SIMULATION AND THE OPTIMIZER.
def CONTROLLER(l_Materials, d_regions, d_LowerBoundGrade, d_LowerBoundSize, \
                d_UpperBoundGrade, d_UpperBoundSize, d_RegionMass, d_WeightGrades, \
                df_Truck, df_Discharge, df_LoadingMachine, l_Regions, v_WasteName, v_MaterialsName, v_MassName,
                v_optimization_time, \
                v_simulation_time, v_rem, m_df_usina, d_Perfom_plant, df_LoadTime_truck, df_UnloaTime_truck,
                df_EmpHaulage_truck, df_LoadHaulage_truck, \
                df_MainBetTime_plant, df_MainDurTime_plant, df_MainBetTime_truck, df_MainDurTime_truck, df_ShiftTurn, \
                df_Refueling, df_MovTime_loader, d_MinMaxGrades, d_MinMaxSizes, df_MainBetTime_loader,
                df_MainDurTime_loader, df_LocalComp, \
                df_Random, df_RandDurTime, Path, v_prioritization, v_tolerance, OutputPath, m_v_num_rep,
                m_v_start_rep):
    c_d_TDE = {}
    # ASSIGN TO THE DICTIONARY C_D_TDE THE MOVEMENT TIMES OF THE LOADING MACHINES BETWEEN THE MINE REGIONS. THIS DICIONARY IS AN INPUT OF THE MILP MODEL
    for i in df_MovTime_loader.index:
        aux = eval(i)
        c_d_TDE[aux] = int(df_MovTime_loader['Tempo'].loc[i])

    animation = True  # GENERATES ALIVE GRAPHS DURATION THE EXECUTION OF THE SIMULATION
    if animation:
        plt.ion()
        fig, ((ax00, ax01), (ax10, ax11)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.tight_layout(pad=3.0)
        plt.show(block=False)

    l_repl = []  # LIST THAT STORES EACH SIMULATION REPLICATION OBJECT
    c_cont_repl = m_v_start_rep - 1
    for i in range(m_v_num_rep):
        l_repl.append(SIMULATION())

    # THIS LOOP IS EXECUTED UNTIL ALL REPLICATIONS HAS BEEN DONE.
    while len(l_repl) > 0:
        c_cont_repl += 1  # VARIABLE THAT STORES THE NUMBER OF PERFORMED REPLICATIONS
        global o_l_materials
        global o_l_FreeMMUIndex
        global c_d_CycleTime
        o_l_FreeMMUIndex = []  # LIST THAT STORES THE INDEXES OF MINE REGIONS
        o_l_materials = l_Materials  # LIST THAT STORES THE MATERIALS OF THE FREE MMUS,
        s = l_repl[0]  # DECLARES THE ACTUAL SIMULATION OBJECT AS S
        s.Path = Path  # ASSIGN THE PATH TO BE SAVED THE DATA OF THE SMULATION
        s.RepNumber = c_cont_repl  #
        s.OutputPath = OutputPath
        s.d_WeightGrades = d_WeightGrades
        s.v_TotalScheduledTrips = 0  # INITIALIZES THE SIMULATION VARIABLE THAT STORES THE TOTAL NUMBER OF SCHDEUDLE TRIPS
        s.v_TotalPerformedTrips = 0  # INITIALIZES THE SIMULATION VARIABLE THAT COUNT THE TOTAL NUMBER OF PERFORMED TRIPS
        aux1 = []
        aux2 = []

        aux1 = max(df_LoadingMachine['Productivity'].to_list()) * v_optimization_time
        aux2 = max(df_LoadingMachine[
                       'Productivity'].to_list()) * 48  # AUXILIARY VARIABLE THAT STORES THE MAXIMUM AVAILABLE MASS IN THE REGIONS.

        s.clock = 0  # INITIALIZES THE SIMULATION CLOCK

        s.MaxRegionMass = aux1
        s.MaxRegionMass2 = aux2
        MaxMassPerRegion = aux2

        s.InitializesDischarges(df_Discharge)  # INITIALIZES THE DISCHARGE OBJECTS OF THE SIMULATION MODULE
        s.df_MainBetTime_plant = df_MainBetTime_plant  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE TIME BETWEEN BREAKDOWNS OF THE PROCESSING PLANTS
        s.df_MainDurTime_plant = df_MainDurTime_plant  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE BREAKDOWN DURATION TIMES  OF THE PROCESSING PLANTS
        s.df_MainBetTime_truck = df_MainBetTime_truck  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE TIME BETWEEN BREAKDOWNS OF THE TRUCK FLEETS
        s.df_MainDurTime_truck = df_MainDurTime_truck  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE BREAKDOWN DURATION TIMES  OF THE TRUCK FLEETS
        s.df_MainBetTime_loader = df_MainBetTime_loader  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE TIME BETWEEN BREAKDOWNS OF THE LOADING MACHINES
        s.df_MainDurTime_loader = df_MainDurTime_loader  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE BREAKDOWN DURATION TIMES  OF THE LOADING MACHINES
        s.df_ShiftTurn = df_ShiftTurn  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE DURATION TIME OF THE SHIFT CHANGE EVENT.
        s.df_Refueling = df_Refueling  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE DURATION TIME OF REFUELING EVENT
        s.df_MovTime_loader = df_MovTime_loader  # ASSIGN TO THE SIMULATION DATAFRAME THE DATA OF MOVEMENT TIME OF THE LOADING MACHINES BETWEEN THE REGIONS
        s.df_RandDurTime = df_RandDurTime  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE BREAKDOWN DURATION TIMES  OF THE RANDOM EVENTS
        s.df_Random = df_Random  # ASSIGN TO THE SIMULATION DATAFRAME WITH DATA OF THE BETWEEN BREAKDOWN TIMES  OF THE RANDOM EVENTS
        m_df_aux = s.df_Random[(s.df_Random['Equipment'] == 'Trucks')]
        s.d_BetweenRandomEvents_truck = {}
        for i in m_df_aux.index:
            s.d_BetweenRandomEvents_truck[m_df_aux['Event'].loc[i]] = m_df_aux.loc[i]
        m_df_aux = s.df_RandDurTime[(s.df_RandDurTime['Equipment'] == 'Trucks')]
        s.d_RandomEventDuration_truck = {}
        for i in m_df_aux.index:
            s.d_RandomEventDuration_truck[m_df_aux['Event'].loc[i]] = m_df_aux.loc[i]
        m_df_aux = s.df_Random[(s.df_Random['Equipment'] == 'Loaders')]
        s.d_BetweenRandomEvents_loader = {}
        for i in m_df_aux.index:
            s.d_BetweenRandomEvents_loader[m_df_aux['Event'].loc[i]] = m_df_aux.loc[i]
        m_df_aux = s.df_RandDurTime[(s.df_RandDurTime['Equipment'] == 'Loaders')]
        s.d_RandomEventDuration_loader = {}
        for i in m_df_aux.index:
            s.d_RandomEventDuration_loader[m_df_aux['Event'].loc[i]] = m_df_aux.loc[i]

        # INITIALIZES THE OBJECTS THAT REPRESENTS THE MINE EQUIPMENT
        s.InitializesLoaders(df_LoadingMachine)  # INITIALIZES THE LOADING MACHINES
        s.TrucksArrivals(df_Truck)  # INITIALIZES THE TRUCKS
        s.InitializesOrePlants(m_df_usina)  # INITIALIZES THE PROCESSING PLANTS
        s.InitializesReclaimCheck()  # INITIALIZE THE ROUTINE THAT CONTROLS THE TIME INTERVAL TO RECLAIM THE FORMED PILES IN THE ORE YARD.
        s.d_Perfom_plant = d_Perfom_plant
        s.df_LoadTime_truck = df_LoadTime_truck  # ASSIGN TO THE SIMULATION DATAFRAME THE LOADING TIMES OF THE TRUCKS' CYCLES
        s.df_UnloaTime_truck = df_UnloaTime_truck  # ASSIGN TO THE SIMULATION DATAFRAME THE UNLOADING TIMES OF THE TRUCKS' CYCLES
        s.df_EmpHaulage_truck = df_EmpHaulage_truck  # ASSIGN TO THE SIMULATION DATAFRAME THE UNLOADING EMPTY HAULAGE OF THE TRUCKS' CYCLES
        s.df_LoadHaulage_truck = df_LoadHaulage_truck  # ASSIGN TO THE SIMULATION DATAFRAME THE LOADED HAULAGE OF THE TRUCKS' CYCLES
        s.OptimizationTime = v_optimization_time  # ASSIGN TO THE SIMULATION VARIABLE THE DURATION TIME OF OPTIMIZATION

        # RECORDED THE AVERAGE CYCLE TIME OF THE TRUCKS
        c_d_CycleTime = {}
        for i in range(len(df_EmpHaulage_truck)):
            c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                           df_EmpHaulage_truck['Destination'].iloc[i])] = 0
            for j in range(0, 10):
                c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                               df_EmpHaulage_truck['Destination'].iloc[i])] += s.GeneratesEmptyHaulageTime(
                    df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                    df_EmpHaulage_truck['Destination'].iloc[i])
                c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                               df_EmpHaulage_truck['Destination'].iloc[i])] += s.GeneratesLoadedHaulageTime(
                    df_LoadHaulage_truck['Fleet'].iloc[i], df_LoadHaulage_truck['Origin'].iloc[i],
                    df_LoadHaulage_truck['Destination'].iloc[i])
            c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                           df_EmpHaulage_truck['Destination'].iloc[i])] = \
                c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                               df_EmpHaulage_truck['Destination'].iloc[i])] / 10
            c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                           df_EmpHaulage_truck['Destination'].iloc[i])] += s.GeneratesLoadingTime(
                df_LoadingMachine['ID'].iloc[0], df_Truck['ID'].iloc[0])
            c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                           df_EmpHaulage_truck['Destination'].iloc[i])] += s.GeneratesUnloadingTime(df_Truck['ID'].iloc[0],
                                                                                            df_Discharge['ID'].iloc[0])
            c_d_CycleTime[(df_EmpHaulage_truck['Fleet'].iloc[i], df_EmpHaulage_truck['Origin'].iloc[i],
                           df_EmpHaulage_truck['Destination'].iloc[i])] += 2

        for i in range(len(df_Truck)):
            for j in l_Regions:
                for k in range(len(df_Discharge)):
                    if (df_Truck['ID'].iloc[i], j, df_Discharge['ID'].iloc[k]) not in c_d_CycleTime.keys():
                        c_d_CycleTime[(df_Truck['ID'].iloc[i], j, df_Discharge['ID'].iloc[k])] = float(
                            df_Truck['Ciclo'].iloc[i])
                        df_EmpHaulage_truck = df_EmpHaulage_truck.append(
                            {'ID': len(df_EmpHaulage_truck), 'Fleet': df_Truck['ID'].iloc[i], \
                             'Origin': j, 'Destination': df_Discharge['ID'].iloc[k],
                             'Expression': 'NORM',
                             'Param_1': float(df_Truck['Ciclo'].iloc[i]) / 2, 'Param_2': 0.5,
                             'Param_3': 'nan'}, ignore_index=True)
                        df_LoadHaulage_truck = df_LoadHaulage_truck.append(
                            {'ID': len(df_LoadHaulage_truck), 'Fleet': df_Truck['ID'].iloc[i], \
                             'Origin': j, 'Destination': df_Discharge['ID'].iloc[k],
                             'Expression': 'NORM',
                             'Param_1': float(df_Truck['Ciclo'].iloc[i]) / 2, 'Param_2': 0.5,
                             'Param_3': 'nan'}, ignore_index=True)
        s.df_EmpHaulage_truck = df_EmpHaulage_truck
        s.df_LoadHaulage_truck = df_LoadHaulage_truck
        d_LastAlocation = {}
        for i in df_LoadingMachine.index:
            d_LastAlocation[i] = 0
        m_d_PlantRate = {}

        # INITIALIZES THE STATUS OF THE INITIAL ORE PILE IN THE ORE YARD.
        for i in s.d_DiscResource.keys():
            m_d_PlantRate[i] = s.d_DiscResource[i].produt
            if s.d_DiscResource[i].Type == 1:
                s.PileIndex += 1
                s.d_Piles[s.PileIndex] = s.Piles(s.PileIndex, s.d_DiscResource[i].id,
                                                  s.d_DiscResource[i].BatchMass, 0, 0, 1)
                s.d_DiscResource[i].d_PileStatus["Stacking"] = s.PileIndex
                s.d_DiscResource[i].d_PileStatus["Reclaiming"] = 0
                s.d_DiscResource[i].d_PileStatus["Waiting"] = 0
                s.d_Piles[s.PileIndex].Stacking = 1
                s.d_Piles[s.PileIndex].Reclaiming = 0
                s.d_Piles[s.PileIndex].Waiting = 0
                s.d_Piles[s.PileIndex].quality['Global'] = 0
                for j in d_WeightGrades.keys():
                    s.d_Piles[s.PileIndex].quality[j] = 0
                s.d_DiscResource[i].Pile = s.PileIndex

        c_v_TotalMass = 0
        c_d_ScheduledMassPerRegion = []
        for i in d_regions.keys():
            s.s_d_RegionMass[i] = []
            for j in range(len(d_regions[i])):
                s.s_d_RegionMass[i].append(d_regions[i][v_MassName].iloc[j])
            c_v_TotalMass += sum(d_RegionMass[i])
            s.ExtracMassRegion[i] = 0
            c_d_ScheduledMassPerRegion.append(sum(d_RegionMass[i]))

        o_d_razao_regioes = {}
        for i in d_RegionMass.keys():
            o_d_razao_regioes[i] = [sum(d_RegionMass[i]) / c_v_TotalMass, sum(d_RegionMass[i]), 0]

        global tempo_graph
        tempo_graph = []
        global c_l_hist_rem
        c_l_hist_rem = []
        c_d_DischargeProductivity = {}
        for i in df_Discharge.index:
            c_d_DischargeProductivity[i] = df_Discharge["Productivity"].loc[i]

        v_WasteMassAvail = 0
        v_OreMassAvail = 0
        c_d_prog_mes = {0: 0, 24: 0, 53: 0, 84: 0, 114: 0, 145: 0, 175: 0, 206: 0, 237: 0, 267: 0, 298: 0, 328: 0}
        c_l_files = ["\TruckEvents" + str(c_cont_repl) + ".txt", "\LoaderEvents" + str(c_cont_repl) + ".txt",
                     "\OrePiles" + str(c_cont_repl) + ".txt", "\Trips" + str(c_cont_repl) + ".txt"]
        for i in c_l_files:
            if os.path.exists(OutputPath + i):
                os.remove(OutputPath + i)
        s.TrucksEventFile = open(OutputPath + "\TruckEvents" + str(c_cont_repl) + ".txt", 'a')
        s.TrucksEventFile.write(
            'fleet,truck,activitie,clock,other,duration\n')
        s.TrucksEventFile.close()
        s.TrucksEventFile = open(OutputPath + "\Trips" + str(c_cont_repl) + ".txt", 'a')
        s.TrucksEventFile.write(
            'clock,origin,material,destination,payload\n')
        s.TrucksEventFile.close()
        s.d_LowerBoundSize = d_LowerBoundSize

        # INITIALIZES THE VARIABLE THAT CONTROLS WHEN A MONTH FINSIHES AND STARTS THE NEXT MONTH:
        c_passou_mes = False

        # LOOP WHOSE INSIDE COMMANDS SELECT THE FREE MMUS, ORDER THE PRIORITIZATION OF THE OBJECTIVES, CALL THE MILP SOLVER WHEN NECESSARY, AND ADVANCE THE SIMULATION CLOCK
        while (s.clock <= v_simulation_time and ((v_WasteMassAvail + v_OreMassAvail) > 0)) or (
                s.clock == 0 and s.v_TotalScheduledTrips == 0):
            status = 2
            # CHECK IF THE CRITERIAS TO CALL THE MILP SOLVER IS SATISFIED
            if (s.clock >= s.NextOptimization or s.optimize == 1 or s.v_TotalPerformedTrips > s.v_TotalScheduledTrips):
                print("SIMULATION CLOCK = " + str(round(s.clock / 1440, 2)) + " DAYS")
                s.optimize = 0
                s.NextOptimization = s.clock + v_optimization_time * 60  # ASSIGN THE NEXT SIMULATION TIME.
                # SELECT THE FREE MMUS
                s.o_d_regions, o_l_FreeMMUIndex, NM, v_rem_a, v_WasteMassAvail, v_OreMassAvail = select_freeMMUS(
                    d_regions, s.s_d_RegionMass, l_Regions, v_MaterialsName, v_WasteName, v_MassName \
                    , MaxMassPerRegion, d_WeightGrades)

                # UPDATES THE RATIO BETEWEEN THE TOTAL EXTRACTED MASS AND THE TOTAL SCHEDULED MASS PER REGION
                for i in d_RegionMass.keys():
                    if i in o_d_razao_regioes.keys():
                        o_d_razao_regioes[i][2] = o_d_razao_regioes[i][1] - sum(s.s_d_RegionMass[i])

                # INITIALIZES THE DICTIONARY THAT RECORDS THE MASS AND ORE GRADES AND PARTICLE SIZES OF THE ORE PILES.
                o_d_PileMasses = {}
                o_d_PileQualities = {}

                for Pile in s.d_Piles.keys():
                    if s.d_Piles[Pile].Stacking == 1:
                        o_d_PileMasses[s.d_Piles[Pile].Discharge] = s.d_Piles[Pile].massa
                        for i in d_WeightGrades.keys():
                            o_d_PileQualities[(s.d_Piles[Pile].Discharge, i)] = s.d_Piles[Pile].quality[i]
                m_PlantTime = {}

                for i in m_df_usina.index:
                    if s.d_Plants[i].status == 0:
                        if s.d_Plants[i].MainFinalEvent > (s.clock + v_optimization_time * 60):
                            m_PlantTime[i] = 0
                        else:
                            m_PlantTime[i] = (s.clock + v_optimization_time * 60) - s.d_Plants[i].MainFinalEvent
                    else:
                        if s.d_Plants[i].MainFinalEvent > (s.clock + v_optimization_time * 60):
                            m_PlantTime[i] = v_optimization_time * 60
                        else:
                            m_PlantTime[i] = s.d_Plants[i].MainFinalEvent - s.clock

                # CHECK FOR EACH DISCHARGE THAT HAS AN ORE YARD UPSTREAM IF THIS YARD IS FULL OR NOT.
                for i in s.d_DiscResource.keys():
                    if s.d_DiscResource[i].Type == 1:
                        df_Discharge["Productivity"].loc[i] = m_d_PlantRate[i]
                        if len(s.d_DiscResource[i].WaitingPiles) == 3:
                            df_Discharge["Productivity"].loc[i] = 0
                print("STRIIPING RATIO = ", round(v_rem_a, 2))

                # CREATES THE ALIVE GRAPHS
                c_l_hist_rem.append(s.WasteMass / max(s.OreMass, 1))
                s.l_MonWasteMass.append(s.WasteMass / 1000000)
                s.l_MonOreMass.append(s.OreMass / 1000000)
                tempo_graph.append(s.clock / 1440)
                if len(tempo_graph) > 20:
                    del c_l_hist_rem[0:10]
                    del s.l_MonWasteMass[0:10]
                    del s.l_MonOreMass[0:10]
                    del tempo_graph[0:10]
                cont = 0
                for i in s.ExtracMassRegion.keys():
                    if s.ExtracMassRegion[i] < sum(d_RegionMass[i]) * 0.95:
                        cont += 1
                cont = 0

                c_l_ind_regioes = tuple(s.ExtracMassRegion.keys())
                c_l_ExtracMassRegion = []
                c_l_ExtracMassRegion = list(s.ExtracMassRegion.values())
                c_l_meses = tuple(s.s_md_prod_mensal.index)
                if animation:
                    c_l_meses_values_ore = s.s_md_prod_mensal['Ore'].tolist()
                    c_l_meses_values_waste = s.s_md_prod_mensal['Waste'].tolist()
                    ax00.clear()
                    ax01.clear()
                    ax10.clear()
                    ax11.clear()
                    ax10.plot(tempo_graph, c_l_hist_rem, marker="o")
                    x_indexes = np.arange(12)
                    width = 0.2
                    ax00.bar(x_indexes, c_l_meses_values_ore, width=width, label="Ore")
                    ax00.bar(x_indexes + width, c_l_meses_values_waste, color="orange", width=width, label="waste")
                    ax11.set_xlim(right=130000)
                    ax01.set_xlim(right=6000000)
                    if len(c_l_ExtracMassRegion) > 0:
                        ax01.barh(c_l_ind_regioes, c_d_ScheduledMassPerRegion, color="orange")
                        ax01.barh(c_l_ind_regioes, c_l_ExtracMassRegion)

                    if s.d_Plants[s.d_DiscResource['WETPLANT'].Plant].status == 0:
                        if s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming'] > 0:
                            if len(s.d_DiscResource['WETPLANT'].WaitingPiles) == 0:
                                ax11.barh(("Stacking " + str(s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']),
                                           "Reclaiming  " + str(
                                               s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']),
                                           "Ore yard mass"), \
                                          [s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']].massa,
                                           s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']].massa,
                                           s.d_Plants[s.d_DiscResource['WETPLANT'].Plant].YardMass],
                                          color=["blue", "red", "grey"])
                            else:
                                ax11.barh(("Stacking " + str(s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']),
                                           "Reclaiming  " + str(
                                               s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']),
                                           "Waiting " + str(s.d_DiscResource['WETPLANT'].WaitingPiles[0]),
                                           "Ore yard mass"), \
                                          [s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']].massa,
                                           s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']].massa,
                                           s.d_Piles[s.d_DiscResource['WETPLANT'].WaitingPiles[0]].massa,
                                           s.d_Plants[s.d_DiscResource['WETPLANT'].Plant].YardMass],
                                          color=["blue", "red", "yellow", "grey"])
                    else:
                        if s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming'] > 0:
                            if len(s.d_DiscResource['WETPLANT'].WaitingPiles) == 0:
                                ax11.barh(("Stacking " + str(s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']),
                                           "Reclaiming  " + str(
                                               s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']),
                                           "Ore yard mass"), \
                                          [s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']].massa,
                                           s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']].massa,
                                           s.d_Plants[s.d_DiscResource['WETPLANT'].Plant].YardMass],
                                          color=["blue", "red", "grey"])
                            else:
                                ax11.barh(("Stacking " + str(s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']),
                                           "Reclaiming " + str(s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']),
                                           "Waiting " + str(s.d_DiscResource['WETPLANT'].WaitingPiles[0]),
                                           "Ore yard mass"), \
                                          [s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Stacking']].massa,
                                           s.d_Piles[s.d_DiscResource['WETPLANT'].d_PileStatus['Reclaiming']].massa,
                                           s.d_Piles[s.d_DiscResource['WETPLANT'].WaitingPiles[0]].massa,
                                           s.d_Plants[s.d_DiscResource['WETPLANT'].Plant].YardMass],
                                          color=["blue", "green", "yellow", "grey"])

                    ax00.set_title("Ore and waste simulated per month. Blue bars = ore")
                    ax00.set_xlabel("Month index")
                    ax00.set_ylabel("Tonnes")
                    ax01.set_title("Planned and simulated mass per mine region. Blue bars = simulated")
                    ax01.set_xlabel("Tonnes")
                    ax10.set_title("Acumulated stripping ratio per day", y=1.0, pad=-14)
                    ax10.set_xlabel("Days")
                    ax11.set_title("Active ore piles in the yard ", y=1.0, pad=-14)
                    ax11.set_xlabel("Tonnes")
                    ax01.xaxis.grid()
                    ax00.yaxis.grid()
                    ax00.spines['right'].set_visible(False)
                    ax00.spines['top'].set_visible(False)
                    ax01.spines['right'].set_visible(False)
                    ax01.spines['top'].set_visible(False)
                    ax10.spines['right'].set_visible(False)
                    ax10.spines['top'].set_visible(False)
                    ax11.spines['right'].set_visible(False)
                    ax11.spines['top'].set_visible(False)
                    plt.show()
                    plt.pause(0.01)

                for i in df_Discharge.index:
                    df_Discharge["Productivity"].loc[i] = c_d_DischargeProductivity[i]

                while status != 1:
                    c_v_RequiredOre = 0
                    for i in df_Discharge.index:
                        s.d_DiscResource[i].status = 1
                        if df_Discharge['Type'].loc[i] == 1:
                            df_Discharge["Productivity"].loc[i] = c_d_DischargeProductivity[i]
                            if ((s.d_DiscResource[i].d_PileStatus["Reclaiming"] != 0 and len(
                                    s.d_DiscResource[i].WaitingPiles) >= 1) or
                                    len(s.d_DiscResource[i].WaitingPiles) >= 2):
                                df_Discharge["Productivity"].loc[i] = 0
                            c_v_RequiredOre += df_Discharge["Productivity"].loc[i] * v_optimization_time

                    s.ThereIsWaste = True
                    # DEFINE THE PRIORITIZATION ORDER OF THE FUNCTIONS ACCORDING TO THE CHOOSEN
                    if (v_OreMassAvail == 0 and v_WasteMassAvail > 0) or (
                            c_v_RequiredOre == 0 and v_WasteMassAvail > 0):
                        o_l_PrioritizationOrder = [0, 0, 0, 0, 0, 0, 0, 10, 9, 8]
                        o_l_weight = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
                    elif v_OreMassAvail > 0 and v_WasteMassAvail == 0:
                        aux = 0
                        for i in df_Discharge.index:
                            if df_Discharge["Type"].loc[i] == 1:
                                aux += int(df_Discharge["Productivity"].loc[i])
                        if aux < 100:
                            for i in df_Discharge.index:
                                if df_Discharge["Type"].loc[i] == 1 and df_Discharge['Relaxar'].loc[i] == "s":
                                    df_Discharge["Productivity"].loc[i] = c_d_DischargeProductivity[i]
                                    aux += df_Discharge["Productivity"].loc[i]
                        s.ThereIsWaste = False
                        if v_prioritization == "Grade":
                            o_l_PrioritizationOrder = [10, 9, 8, 6, 7, 5, 0, 0, 4, 3]
                        elif v_prioritization == "Size":
                            o_l_PrioritizationOrder = [10, 8, 9, 7, 5, 6, 0, 0, 4, 3]
                        elif v_prioritization == "Same":
                            o_l_PrioritizationOrder = [10, 9, 9, 8, 7, 7, 0, 0, 4, 3]
                        else:
                            o_l_PrioritizationOrder = [10, 9, 9, 10, 9, 9, 0, 0, 4, 3]
                        o_l_weight = [1, 1, 1, 1, 1, 1, 0, 0, 1, 1]
                    elif v_OreMassAvail < c_v_RequiredOre and v_WasteMassAvail > v_rem * c_v_RequiredOre:
                        o_l_weight = [1, 1, 1, 1, 1, 1, 1, 0, 1, 1]
                        if v_prioritization == "Grade":
                            o_l_PrioritizationOrder = [10, 9, 8, 6, 7, 5, 0, 11, 4, 3]
                        elif v_prioritization == "Size":
                            o_l_PrioritizationOrder = [10, 8, 9, 6, 5, 7, 0, 11, 4, 3]
                        elif v_prioritization == "Same":
                            o_l_PrioritizationOrder = [10, 9, 9, 8, 7, 7, 0, 11, 4, 3]
                        else:
                            o_l_PrioritizationOrder = [10, 9, 9, 10, 9, 9, 0, 11, 4, 3]
                    elif v_OreMassAvail > c_v_RequiredOre and v_WasteMassAvail > v_rem * c_v_RequiredOre:
                        o_l_weight = [1, 1, 1, 1, 1, 1, 0, 1, 1, 1]
                        if v_prioritization == "Grade":
                            o_l_PrioritizationOrder = [10, 9, 8, 6, 7, 5, 0, 4, 3, 2]
                        elif v_prioritization == "Size":
                            o_l_PrioritizationOrder = [10, 8, 9, 6, 5, 7, 0, 4, 3, 2]
                        elif v_prioritization == "Same":
                            o_l_PrioritizationOrder = [10, 9, 9, 8, 7, 7, 0, 4, 3, 2]
                        else:
                            o_l_PrioritizationOrder = [10, 9, 9, 10, 9, 9, 0, 4, 3, 2]
                    else:
                        o_l_weight = [1, 1, 1, 1, 1, 1, 0, 1, 1, 1]
                        if v_prioritization == "Grade":
                            o_l_PrioritizationOrder = [10, 9, 8, 6, 7, 5, 0, 4, 3, 2]
                        elif v_prioritization == "Size":
                            o_l_PrioritizationOrder = [10, 8, 9, 6, 5, 7, 0, 4, 3, 2]
                        elif v_prioritization == "Same":
                            o_l_PrioritizationOrder = [10, 9, 9, 7, 7, 5, 0, 4, 3, 2]
                        else:
                            o_l_PrioritizationOrder = [10, 9, 8, 7, 6, 5, 0, 4, 3, 2]
                    d_aloc = {}
                    for i in s.d_LoadResource.keys():
                        df_LoadingMachine['Disponibilidade'].loc[i] = s.d_LoadResource[i].disp
                        d_aloc[i] = d_LastAlocation[i]

                    # CALLS THE MILP SOLVER
                    s.d_alocation, s.d_trips, d_LastAlocation, status, s.TripsperLoader, otimizar_teor = otimizador.solve(
                        o_l_materials, df_Truck, df_LoadingMachine, \
                        df_Discharge, d_LowerBoundGrade, d_UpperBoundGrade, \
                        d_LowerBoundSize, d_UpperBoundSize, \
                        s.o_d_regions, o_l_FreeMMUIndex, d_WeightGrades, v_MaterialsName, v_WasteName, v_MassName, \
                        v_optimization_time, v_rem, o_d_PileMasses, o_d_PileQualities, NM, c_d_CycleTime, \
                        m_PlantTime, df_MovTime_loader, d_LastAlocation, d_MinMaxGrades, d_MinMaxSizes, status,
                        o_d_razao_regioes, c_v_TotalMass, o_l_PrioritizationOrder, \
                        df_LocalComp, o_l_weight, v_tolerance)

               # FOR EACH LOADING MACHINE, IF IT IS NOT ITS FIRST ASSIGMENMENT AND IF THE PREVIOUS ASSIGNED REGION IS NOT THE SAME OF THE CURRENT ASSIGNED REGION
                for i in s.d_LoadResource.keys():
                    if (d_aloc[i] != 0 and d_LastAlocation != 0 and (d_aloc[i] != d_LastAlocation[i])):
                        s.d_LoadResource[i].t_deslocando = c_d_TDE[(i, d_LastAlocation[i], d_aloc[i])]
                    else:
                        s.d_LoadResource[i].t_deslocando = 0

                s.d_PerformedTrips = {}  # INITIALES THE DICTIONARY THAT CONTROLLS THE NUMBER OF PERFORMED TRIPS PER ROUTE.
                s.v_TotalPerformedTrips = 0  # INITIALES THE VARIABLE THAT CONTROLLS THE TOTAL NUMBER OF PERFOMED TRIPS
                s.v_TotalScheduledTrips = 0  # INITIALES THE VARIABLE THAT CONTROLLS THE TOTAL NUMBER OF SCHEDULED TRIPS
                for i in s.d_trips.keys():
                    s.d_PerformedTrips[i] = 0
                    s.v_TotalScheduledTrips += s.d_trips[i]  # UPDATES THE TOTAL SCHEDULE TRIPS VARIABLE
                if s.v_TotalScheduledTrips == 0 and s.clock == 0:
                    s.clock = 1
            s.AdvancesClock()
        print("TOTAL RECLAIMED MASS = ", round(s.FeedMass, 0), "TONNES")

        s.s_md_times.to_csv("Resumo_eventos" + str(c_cont_repl) + ".csv")
        dados = {}
        dados = {'dia': [i for i in s.s_d_massas.keys()], 'minerio': [s.s_d_massas[i][0] for i in s.s_d_massas.keys()], \
                 'esteril': [s.s_d_massas[i][1] for i in s.s_d_massas.keys()]}
        pd.DataFrame.from_dict(dados).to_csv(OutputPath + "\Resumo_massas" + str(c_cont_repl) + ".csv")
        s.s_md_times.to_csv(OutputPath + "\Resumo_eventos" + str(c_cont_repl) + ".csv")
        del dados
        del s.s_md_times
        while len(s.d_Piles) > 0:
            for i in s.d_Piles.keys():
                s.d_Piles[i].Reclaiming = 0
                s.d_Piles[i].Stacking = 1
                s.d_Piles[i].Waiting = 0
                del s.d_Piles[i]
                break

        while len(s.d_Plants) > 0:
            for i in s.d_Plants.keys():
                s.d_Plants[i].status == 1
                del s.d_Plants[i]
                break

        while len(s.d_DiscResource) > 0:
            for i in s.d_DiscResource.keys():
                del s.d_DiscResource[i]
                break

        del s.clock
        while len(s.EquipmentList) > 0:
            del s.EquipmentList[0]
            break
        del s
        c_v_RequiredOre = 0
        for i in df_Discharge.index:
            df_Discharge["Productivity"].loc[i] = c_d_DischargeProductivity[i]
            c_v_RequiredOre += df_Discharge['Productivity'].loc[i] * v_optimization_time
        del l_repl[0]
