import sys
import numpy as np
import pandas as pd

class SIMULATION:
    def __init__(self):
        self.clock = 0  # Initializes the simulation clock variable
        self.duration = 0  # Initializes the duration of event's variable
        # Dictionary of resources - Trucks, shovels, and discharges
        self.EquipmentList = [] # List with all equipment objects
        self.d_TruckResource = {}  # Dictionary that stores all truck objects
        self.d_LoadResource = {} # Dictionary that stores all loading machine objects
        self.d_DiscResource = {} # Dictionary that stores all discharge objects
        self.d_deposito = {} # Deposit dictionary. Not implemented yet
        self.d_Piles = {} # Dictionary that stores all pile objects
        self.Event = []  # [tempo,Event,index,Type de equipamento]
        self.NumberTrucks = 0 # Number of trucks in the system
        self.truck = self.Truck(0, 0, 0, 0, 0)
        self.d_alocation = {} # Dicionary that stores assignment of the loading machines at the mine regions
        self.d_trips = {} # Dictionary that stores  the scheduled trips
        self.d_PerformedTrips = {} # Dicionary that stores the performed trips
        self.MaxRegionMass = 0 # Maximum mass per region to be selected as mining candidate
        self.OptimizationTime = 0 # Initializes the optimization time variable
        self.NextOptimization = 0 #Next time to call the optimizer
        self.v_TotalPerformedTrips = 0 # Total number of performed trips
        self.v_TotalScheduledTrips = 0 # Total Number of program trips
        self.duration = 0 # Duration of the work-shift
        self.o_d_regions = {}
        self.s_d_RegionMass = {}
        self.PileIndex = 0 # Index for each formed pile
        self.d_WeightGrades = {} # Weigh to chemical elements
        self.Path = "" # Directory path to save files.
        self.OutputPath = "" # Directory path to save files
        self.RepNumber = 0 # Initializes the current replication index

        # Files paths directories
        self.TripsFile = open(self.OutputPath + "\Trips"+ str(self.RepNumber) + ".txt", 'w') # Stores the details of truck's trips
        self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'w') #Stores the details of truck's events
        self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'w') #Sores the details fo excavator's events
        self.PileFile = open(self.OutputPath + "\OrePiles"+ str(self.RepNumber) + ".txt", 'w') # Stores the mass and other parameters from the piles
        self.PileFile.close()

        self.OreMass = 0 # Count the ore mass performed
        self.WasteMass = 0 # Count the waste mass performed
        self.l_MonOreMass = [] # List of amount of monthly ore mass
        self.l_MonWasteMass = [] # List of amount of monthly waste massa
        self.optimize = 0 # Binary variable, assumes value 1 if its necessary call the solver, and 0 otherwise
        self.d_Plants = {} # Dictionary of the plant's objects


        #Pandas Dataframes of event's times
        self.df_LoadTime_truck = 0
        self.df_UnloaTime_truck = 0
        self.df_EmpHaulage_truck = 0
        self.df_LoadHaulage_truck = 0
        self.d_Distributions = {"TRI": "np.random.triangular(float(Param_1),float(Param_2)),float(Param_3),size = 1)",
                                "NORM": "np.random.normal(float(Param_1),float(Param_2))",
                                "CONT": "self.func_CONT(eval(Param_1),eval(Param_2))",
                                "EXP": "np.random.exponential(float(Param_1))"}
        self.df_MainBetTime_plant = 0
        self.df_MainDurTime_plant = 0
        self.df_MainBetTime_truck = 0
        self.df_MainDurTime_truck = 0
        self.df_MainBetTime_loader = 0
        self.df_MainDurTime_loader = 0
        self.df_ShiftTurn = 0
        self.df_Refueling = 0
        self.df_MovTime_loader = 0
        self.df_RandDurTime = 0
        self.df_Random = 0
        self.FeedMass = 0
        self.ExtracMassRegion = {}
        self.s_md_prod_mensal = pd.DataFrame(columns=["Start", "End", "Ore", "Waste"],
                                             index=["Jan", "Feb", "Marc", "Apr", \
                                                    "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], \
                                             data=[(0, 31, 0, 0), (31, 60, 0, 0), (60, 91, 0, 0), (91, 121, 0, 0),
                                                   (121, 152, 0, 0), (152, 182, 0, 0), (182, 213, 0, 0),
                                                   (213, 244, 0, 0), (244, 274, 0, 0), \
                                                   (274, 305, 0, 0), (305, 335, 0, 0), (335, 365, 0, 0)])
        self.TripsperLoader = {}
        #self.d_entre_eventos_aleatorios_cam = {}
        #self.d_durac_eventos_aleatorios_cam = {}
        self.s_md_times = pd.DataFrame(columns=['Fleet','Day',1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12],
                                    index=[], \
                                    data=[])
        self.s_d_massas = {}
        self.l_index_Times = []
        self.d_LowerBoundSize = 0
        self.ThereIsWaste = True

    #Parental class
    class Equipment:
        def __init__(self, a_id ):
            self.Event = 1 # Key for a dictionary of events, see self.Events
            self.NextEvent = 1 # Attribute that stores the next happening event to a piece of equipment
            self.EventDuration = 0 # Duration time of an activitie
            self.EventEnd = 0 # Start time of the next event.

    #Truck's class declaration
    class Truck(Equipment):
        def __init__(self, Fleet, Mine, a_id, ton, local):
            self.Fleet = Fleet # Fleet identification
            self.Mine = Mine # Mine identification
            self.Capacity = ton # Payload
            self.local = local
            self.Loader = 0 # #Index of an assigned excavator
            self.Discharge = 0 # Index of an assigened discharge
            self.Region = 0
            self.Type = "Caminhão" #Type of equipment
            # Dic of main events
            self.Events = {1: "EmptyHaulage", 2: "ManueverLoader", 3: "LoaderQueue", 4: "Loading", \
                            5: "LoadedHaulage", 6: "DischargeQueue", 7: "Unloading", 8: "TruckMaintenance",
                            9: "ShiftTurn", 10: "FuelSupply", 11:"OtherEvents",100:"Rate_Discharge"}

            self.MainFinalEvent_Truck = 0
            self.Front = 0 #
            self.Material = 0
            self.quality = {}
            self.index = 0
            self.TimeBetweenQueue = 0
            self.TimeBetweenQueue_Disc = 0
            self.autonomy = 0
            self.d_RandomFinalEvent_Truck = {}

    class Escavadeira(Equipment):
        def __init__(self, a_id, produt, fixar_esteril, t_entre_Fronts, cava, disp, Front):
            self.EventDuration = 0
            self.a_id = a_id
            self.cava = cava
            self.disp = disp
            self.Front = Front
            self.queue = []
            self.index = 0
            self.loading = 0
            self.MainFinalEvent_Loader = float('inf')
            self.MainEventDuration_Loader = 0
            self.NextMainEvent_Loader = 0
            self.MainFinalEvent = float('inf')
            self.Events = {1: "LoaderMaintenance", 2: "LoaderFuelSupply", 3: "LoaderMovement", 4:"LoaderShiftTurn",5:"NoAllocation",6: "LoaderWorking",7:"LoaderOtherEvents"}
            self.autonomy = 200
            self.t_movement = 0
            self.HasStop = 0
            self.d_EventEnd_alea_esc = {}
            self.QueueAverTime = 0
            self.QueueAverNumber = 0
            self.InRoute = 0

    class Discharge(Equipment):
        def __init__(self, a_id, produt, HasPile, Type, max_queue, max_basculo, BatchMass, prioridade, massa):
            self.id = a_id
            self.produt = produt
            self.HasPile = HasPile
            self.Pile = 0
            self.Type = Type
            #self.max_queue = max_queue
            #self.max_basculo = max_basculo
            self.massa = massa
            self.BatchMass = BatchMass
            self.num = 0
            self.status = 1
            self.Pile = 0
            self.quality = {}
            self.index = 0
            self.Plant = 0
            self.queue = []
            self.Unloading = 0
            self.MainFinalEvent = 10000000
            self.d_PileStatus = {"Reclaiming": 0, "Stacking": 0, "Aguardando": 0}
            self.Events = {1:"Operando",2:"Processando",3:"Manutenção"}
            self.UnloadingTime = 0
            self.DischargeMass = 0
            self.WaitingPiles = []

    class Piles:
        def __init__(self, index, Discharge, Capacity, massa, Reclaiming, Stacking):
            self.index = index
            self.Rate = 0
            self.Quantity = 0
            self.Capacity = Capacity
            self.massa = massa
            self.Reclaiming = Reclaiming
            self.Stacking = Stacking
            self.Waiting = 0
            self.quality = {}
            #self.tempo_finalizada = 0
            self.Discharge = Discharge
            self.inicio = 0

    class Usina:
        def __init__(self, index, Discharge, Rate, YardCapacity):
            self.index = index
            self.Rate = Rate
            self.Discharge = Discharge
            self.status = 0  # 0 = em manuten  o, 1 = operando
            self.Event = 1
            self.EventDuration = 0
            self.NextEvent = 1
            self.EventEnd = 0
            self.Events = {101: "Reclaim_Pile", 102: "PlantMaintenance"}
            self.YardMass = 0
            self.FullYard = 0
            self.YardCapacity = YardCapacity
            self.EventDuration_man = 0
            self.NextEvent_man = 0
            self.MainFinalEvent = 0
            self.prox_man =0

    class Deposito:
        def __init__(self):
            self.index = ""
            self.Discharge = ""
            self.Capacity = ""
            self.quality = {}
            self.Types = []
            self.massa = 0

    class Check_retomada:
        def __init__(self):
            self.duration = 0
            self.Event = 101
            self.EventDuration = 0
            self.NextEvent = 101
            self.EventEnd = 0
            self.Events = {101: "Reclaim_Pile"}

    #TIME GENERATION

    def func_CONT(self, Param_1, Param_2):
        Param_1 = [float(i) for i in Param_1 if i != Param_1[0]]
        Param_2 = [float(i) for i in Param_2 if i != Param_2[0]]
        s_aux = [0]
        for i in range(1, len(Param_1)):
            s_aux.append(Param_1[i] - Param_1[i - 1])
        Interval = 0
        s_aux[0] = 1-sum(s_aux)
        Interval = np.random.choice(len(Param_2), 1, p=s_aux)
        Interval = int(Interval)
        s_num = float(np.random.rand(1))
        s_num = Param_2[Interval - 1] + (Param_2[Interval] - Param_2[Interval - 1]) * s_num
        return (s_num)

    def gera_num_aleatorio(self, Dist, Param_1, Param_2, Param_3):
        return eval(self.d_Distributions[Dist])

    def gera_tempo_carga(self, Loader, Fleet):
        Expression = self.df_LoadTime_truck['Expressao'][
            (self.df_LoadTime_truck['Carga'] == Loader) & (self.df_LoadTime_truck['Frota'] == Fleet)].iloc[0]
        Param_1 = self.df_LoadTime_truck['Param_1'][
            (self.df_LoadTime_truck['Carga'] == Loader) & (self.df_LoadTime_truck['Frota'] == Fleet)].iloc[0]
        Param_2 = self.df_LoadTime_truck['Param_2'][
            (self.df_LoadTime_truck['Carga'] == Loader) & (self.df_LoadTime_truck['Frota'] == Fleet)].iloc[0]
        Param_3 = self.df_LoadTime_truck['Param_3'][
            (self.df_LoadTime_truck['Carga'] == Loader) & (self.df_LoadTime_truck['Frota'] == Fleet)].iloc[0]
        valor = eval(self.d_Distributions[Expression])
        return valor

    def gera_tempo_basculo(self, Fleet, Discharge):
        Expression = self.df_UnloaTime_truck['Expressao'][
            (self.df_UnloaTime_truck['Descarga'] == Discharge) & (self.df_UnloaTime_truck['Frota'] == Fleet)].iloc[0]
        Param_1 = self.df_UnloaTime_truck['Param_1'][
            (self.df_UnloaTime_truck['Descarga'] == Discharge) & (self.df_UnloaTime_truck['Frota'] == Fleet)].iloc[0]
        Param_2 = self.df_UnloaTime_truck['Param_2'][
            (self.df_UnloaTime_truck['Descarga'] == Discharge) & (self.df_UnloaTime_truck['Frota'] == Fleet)].iloc[0]
        Param_3 = self.df_UnloaTime_truck['Param_3'][
            (self.df_UnloaTime_truck['Descarga'] == Discharge) & (self.df_UnloaTime_truck['Frota'] == Fleet)].iloc[0]
        valor = eval(self.d_Distributions[Expression])
        return valor

    def gera_tempo_viagem_vazio(self, Fleet, origem, Discharge):
        self.df_EmpHaulage_truck.to_csv(self.Path + "/teste.csv", index=False, header=True)
        Expression = self.df_EmpHaulage_truck['Expressao'][
            (self.df_EmpHaulage_truck['Destino'] == Discharge) & (self.df_EmpHaulage_truck['Frota'] == Fleet) & (
                   self.df_EmpHaulage_truck['Origem'] == origem)].iloc[0]
        Param_1 = self.df_EmpHaulage_truck['Param_1'][
            (self.df_EmpHaulage_truck['Destino'] == Discharge) & (self.df_EmpHaulage_truck['Frota'] == Fleet) & (
                    self.df_EmpHaulage_truck['Origem'] == origem)].iloc[0]
        Param_2 = self.df_EmpHaulage_truck['Param_2'][
            (self.df_EmpHaulage_truck['Destino'] == Discharge) & (self.df_EmpHaulage_truck['Frota'] == Fleet) & (
                    self.df_EmpHaulage_truck['Origem'] == origem)].iloc[0]
        Param_3 = self.df_EmpHaulage_truck['Param_3'][
            (self.df_EmpHaulage_truck['Destino'] == Discharge) & (self.df_EmpHaulage_truck['Frota'] == Fleet) & (
                    self.df_EmpHaulage_truck['Origem'] == origem)].iloc[0]
        valor = eval(self.d_Distributions[Expression])
        return valor

    def gera_tempo_viagem_cheio(self, Fleet, origem, Discharge):
        Expression = self.df_LoadHaulage_truck['Expressao'][
            (self.df_LoadHaulage_truck['Destino'] == Discharge) & (self.df_LoadHaulage_truck['Frota'] == Fleet) & (
                    self.df_LoadHaulage_truck['Origem'] == origem)].iloc[0]
        Param_1 = self.df_LoadHaulage_truck['Param_1'][
            (self.df_LoadHaulage_truck['Destino'] == Discharge) & (self.df_LoadHaulage_truck['Frota'] == Fleet) & (
                    self.df_LoadHaulage_truck['Origem'] == origem)].iloc[0]
        Param_2 = self.df_LoadHaulage_truck['Param_2'][
            (self.df_LoadHaulage_truck['Destino'] == Discharge) & (self.df_LoadHaulage_truck['Frota'] == Fleet) & (
                    self.df_LoadHaulage_truck['Origem'] == origem)].iloc[0]
        Param_3 = self.df_LoadHaulage_truck['Param_3'][
            (self.df_LoadHaulage_truck['Destino'] == Discharge) & (self.df_LoadHaulage_truck['Frota'] == Fleet) & (
                    self.df_LoadHaulage_truck['Origem'] == origem)].iloc[0]
        valor = eval(self.d_Distributions[Expression])
        return valor

    def gera_tempo_disponivel_descarga(self):
        return np.random.normal(50, 10)

    def gera_tempo_parada_Discharge(self):
        return np.random.normal(20, 2)

    #Write files:
    def write_file(self, arquivo, Fleet, index, Event, Loader, duration):
        self.TrucksEventFile = open(self.OutputPath + arquivo,'a')
        self.TrucksEventFile.write( Fleet + ',Truck_' + str(index) + "," + str(Event) + "," + "{:.2f}".format(
            self.clock) + "," + Loader + "," + str("{:.2f}".format(duration)) + '\n')
        self.TrucksEventFile.close()



    #Start resources

    def inicia_check_retomada(self):
        check_retomada = self.Check_retomada()
        check_retomada.NextEvent = 101
        check_retomada.EventEnd = self.clock + 10
        self.EquipmentList.append(check_retomada)

    def inicia_escavadeiras(self, m_df_escavadeira):

        for i in list(m_df_escavadeira.index):
            aux_list = []
            aux_list = list(m_df_escavadeira.loc[i])
            self.d_LoadResource[m_df_escavadeira['ID'].loc[i]] = self.Escavadeira(aux_list[0], aux_list[1],
                                                                                     aux_list[2], aux_list[3],
                                                                                     aux_list[4], aux_list[5], 0)
            self.d_LoadResource[m_df_escavadeira['ID'].loc[i]].index = len(self.d_LoadResource)
            escavadeira = self.d_LoadResource[i]

            escavadeira.NextEvent = 3
            escavadeira.EventEnd = np.random.normal(1, 0.5)
            if not self.df_MainBetTime_loader.empty:
                escavadeira.MainFinalEvent_Loader = self.clock + \
                                                   self.gera_num_aleatorio(
                                                       self.df_MainBetTime_loader.loc[i]["Expressao"],
                                                       self.df_MainBetTime_loader.loc[i]["Param_1"], \
                                                       self.df_MainBetTime_loader.loc[i]["Param_2"],
                                                       self.df_MainBetTime_loader.loc[i]["Param_3"])
            else:
                escavadeira.MainFinalEvent_Loader = float('inf')
            self.EquipmentList.append(escavadeira)

            for k in self.d_entre_eventos_aleatorios_esc.keys():
                escavadeira.d_EventEnd_alea_esc[k] = self.clock + \
                                                 self.gera_num_aleatorio(
                                                     self.d_entre_eventos_aleatorios_esc[k]["Expressao"],
                                                     self.d_entre_eventos_aleatorios_esc[k]["Param_1"], \
                                                     self.d_entre_eventos_aleatorios_esc[k]["Param_2"],
                                                     self.d_entre_eventos_aleatorios_esc[k]["Param_3"])

    def inicia_descargas(self, m_df_Discharge):
        for i in list(m_df_Discharge.index):
            aux_list = []
            aux_list = list(m_df_Discharge.loc[i])
            self.d_DiscResource[i] = self.Discharge(aux_list[0], aux_list[1], aux_list[2], aux_list[3], aux_list[4],
                                                   aux_list[5], aux_list[6], aux_list[7], aux_list[8])
            self.d_DiscResource[i].index = len(self.d_DiscResource)

    def inicia_depositos(self, m_df_deposito):
        for i in list(m_df_deposito.index):
            self.d_deposito[i] = self.Deposito()
            self.d_deposito[i].Capacity = m_df_deposito["Capacidade"].loc[i]
            self.d_deposito[i].Discharge = m_df_deposito["Descarga"].loc[i]
            self.d_deposito[i].Types= m_df_deposito["Tipos"].loc[i].split(";")
            self.d_deposito[i].index = m_df_deposito["ID"].loc[i]
            self.d_deposito[i].quality['Global'] = 100

    #Trucks functions
    def entre_chegadas_caminhoes(self, m_df_caminhao):
        tempo = 0
        for i in range(len(m_df_caminhao)):
            for j in range(int(m_df_caminhao['Quant.'].iloc[i])):
                tempo += np.random.normal(1, 0.5)
                self.NumberTrucks += 1
                self.d_TruckResource[self.NumberTrucks] = self.Truck(m_df_caminhao['ID'].iloc[i],
                                                                                    1,\
                                                                                    self.NumberTrucks - 1,
                                                                                    m_df_caminhao['Payload'].iloc[i], 0)

                # m_df_caminhao['Cava'].iloc[i],

                Truck = self.d_TruckResource[self.NumberTrucks]
                Truck.EventDuration = tempo
                Truck.NextEvent = 1
                Truck.EventEnd = self.clock + tempo
                if not self.df_MainBetTime_truck.empty:
                    Truck.MainFinalEvent_Truck = self.clock + \
                                               self.gera_num_aleatorio(
                                                   self.df_MainBetTime_truck.loc[Truck.Fleet]["Expressao"],
                                                   self.df_MainBetTime_truck.loc[Truck.Fleet]["Param_1"], \
                                                   self.df_MainBetTime_truck.loc[Truck.Fleet]["Param_2"],
                                                   self.df_MainBetTime_truck.loc[Truck.Fleet]["Param_3"])
                else:
                    Truck.MainFinalEvent_Truck = float('inf')

                self.d_TruckResource[self.NumberTrucks].index = len(self.d_TruckResource)
                self.EquipmentList.append(self.d_TruckResource[self.NumberTrucks])
                if not self.df_Refueling.empty:
                    Truck.autonomy = self.gera_num_aleatorio("NORM", self.df_Refueling['Autonomy'][
                        (self.df_Refueling['ID'] == Truck.Fleet)], 5, 0)
                else:
                    Truck.autonomy = float('inf')
                for k in self.d_entre_eventos_aleatorios_cam.keys():
                    Truck.d_RandomFinalEvent_Truck[k] = self.clock + \
                                           self.gera_num_aleatorio(
                                               self.d_entre_eventos_aleatorios_cam[k]["Expressao"],
                                               self.d_entre_eventos_aleatorios_cam[k]["Param_1"], \
                                               self.d_entre_eventos_aleatorios_cam[k]["Param_2"],
                                               self.d_entre_eventos_aleatorios_cam[k]["Param_3"])

    def EmptyHaulage(self, Truck):
        # Define qual puml ser  lavrada:
        express1 = "self.o_d_regions[(i[1], i[2])]['Independent_']"
        express2 = "self.o_d_regions[(i[1], i[2])]['Posicao']"
        if [Truck.Fleet,int(self.clock//1440)] not in self.l_index_Times:
            self.l_index_Times.append([Truck.Fleet,int(self.clock//1440)])
            self.s_md_times = self.s_md_times.append(pd.Series(data= {'Fleet':Truck.Fleet,'Day':int(self.clock//1440),\
            1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0}, name=len(self.l_index_Times)), ignore_index= False)
            #print(self.s_md_times)
            #print(self.clock)
        if len(self.d_trips) == 0:
            Truck.Event = 10
            Truck.duration = self.NextOptimization - self.clock
            Truck.EventEnd = self.NextOptimization
            Truck.NextEvent = 1
            self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+str(self.RepNumber)+".txt", 'a')

            self.TrucksEventFile.write(
                Truck.Fleet + ',Truck_'+str(Truck.index) + "," + str(Truck.Event) + "," + "{:.1f}".format(
                    self.clock) + "," + "Sem Material" + "," + str("{:.2f}".format(Truck.duration)) +'\n')
            self.TrucksEventFile.close()
        else:
            DispatchWeights = [100, 10, 100, 1000, 1000, 1000]
            Next_route = [(DispatchWeights[0] * (self.d_PerformedTrips[i] / (self.d_trips[i] + 0.01)) + \
                           DispatchWeights[1] * (len(self.d_LoadResource[i[4]].queue) + self.d_LoadResource[i[4]].InRoute) +\
                           DispatchWeights[2] * (i[3] != Truck.Fleet) +\
                           DispatchWeights[3] * (self.s_d_RegionMass[eval(express1)][eval(express2)] < Truck.Capacity)) + \
                           DispatchWeights[4] * (self.d_LoadResource[i[4]].disp == 0 or self.d_LoadResource[i[4]].HasStop==1) + \
                           DispatchWeights[5] * (self.d_DiscResource[i[0]].Type == 1 and self.d_DiscResource[i[0]].status == 0)  for i in self.d_trips.keys()]
            Minimum = min(Next_route)
            if Minimum >= 1000:
                Truck.Event = 12
                Truck.duration = self.NextOptimization - self.clock
                Truck.EventEnd = self.NextOptimization
                Truck.NextEvent = 1
                self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                self.TrucksEventFile.write(
                    Truck.Fleet + ',Truck_'+ str(Truck.index) + "," + str(Truck.Event) + "," + "{:.1f}".format(
                        self.clock) + "," + "Lack of dispach" + "," + str("{:.2f}".format(Truck.duration)) +'\n')
                self.TrucksEventFile.close()
            else:
                index = Next_route.index(Minimum)
                chaves = list(self.d_trips.keys())
                lista = []
                lista = chaves[index]
                Truck.Front = lista[1]
                Truck.Discharge = str(lista[0])
                Truck.Material = str(lista[2])
                Truck.origem = Truck.Front.split("#")
                Truck.origem = Truck.origem[0] + "#" + Truck.origem[1]
                Truck.duration = self.gera_tempo_viagem_vazio(Truck.Fleet, Truck.origem, Truck.Discharge)
                Truck.Event = 1
                Truck.EventEnd = self.clock + Truck.duration
                Truck.NextEvent = Truck.Event + 1
                try:
                    #Truck.Loader = next(i for i in self.d_alocation.keys() if Truck.Front == self.d_alocation[i])
                    Truck.Loader = next(i for i in self.d_alocation.keys() if self.d_alocation[i] in Truck.Front )
                except StopIteration:
                    Truck.Event = 10
                    Truck.duration = self.NextOptimization - self.clock
                    Truck.EventEnd = self.NextOptimization
                    Truck.NextEvent = 1
                    Truck.Loader = None
                independente = self.o_d_regions[(Truck.Front, Truck.Material)]['Independent_']
                posicao = self.o_d_regions[(Truck.Front, Truck.Material)]['Posicao']
                self.d_LoadResource[Truck.Loader].InRoute +=1
                if Truck.Material != 'DEP':
                    massa = self.s_d_RegionMass[independente][posicao]
                    self.ExtracMassRegion[independente] += Truck.Capacity
                    self.s_d_RegionMass[independente][posicao] = massa - Truck.Capacity
                else:
                    self.d_deposito[Truck.Front].massa -= Truck.Capacity
                if Minimum < 100:
                    self.d_PerformedTrips[
                        (Truck.Discharge, Truck.Front, str(Truck.Material), str(Truck.Fleet), str(Truck.Loader))] += 1
                else:
                    for i in self.d_TruckResource.keys():
                        if (Truck.Discharge, Truck.Front, str(Truck.Material), str(i),
                            str(Truck.Loader)) in self.d_PerformedTrips.keys():
                            self.d_PerformedTrips[
                                (Truck.Discharge, Truck.Front, str(Truck.Material), str(i), str(Truck.Loader))] += 1

                self.v_TotalPerformedTrips += 1
                aux = self.s_md_prod_mensal[(self.clock / 1440 >= self.s_md_prod_mensal["Start"]) & \
                                            (self.clock / 1440 < self.s_md_prod_mensal["End"])]
                aux = aux.index
                aux = aux[0]
                if self.d_DiscResource[Truck.Discharge].Type == 1:
                    self.s_md_prod_mensal['Ore'].loc[aux] += Truck.Capacity
                else:
                    self.s_md_prod_mensal['Waste'].loc[aux] += Truck.Capacity

                for i in self.d_WeightGrades.keys():
                    Truck.quality[i] = [self.o_d_regions[(Truck.Front, Truck.Material)][i],
                                        self.o_d_regions[(Truck.Front, Truck.Material)][self.d_WeightGrades[i]]]
                Truck.autonomy = Truck.autonomy - Truck.duration / 60
                self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                self.TrucksEventFile.write(
                    Truck.Fleet + ',Truck_'+ str(Truck.index) + "," + str(Truck.Event) + "," + "{:.1f}".format(self.clock) + "," + Truck.origem + "," + str("{:.2f}".format(Truck.duration)) +'\n')
                self.TrucksEventFile.close()
            self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (self.s_md_times['Day'] == int(self.clock//1440))]+= Truck.duration

    def ManueverLoader(self, Truck):
        Truck.Event = 2
        Truck.duration = 0.5
        Truck.EventEnd = self.clock + Truck.duration
        Truck.NextEvent = Truck.Event + 1
        Truck.autonomy = Truck.autonomy - Truck.duration / 60
        self.write_file("\TruckEvents"+str(self.RepNumber)+".txt", Truck.Fleet, Truck.index, Truck.Event, Truck.Loader, Truck.duration)
        self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (
                self.s_md_times['Day'] == int(self.clock // 1440))] += Truck.duration

    def LoaderQueue(self, Truck):
        if len(self.d_LoadResource[Truck.Loader].queue) > 0 or self.d_LoadResource[Truck.Loader].loading == 1:
            self.d_LoadResource[Truck.Loader].queue.append(Truck.index)
            Truck.Event = 3
            Truck.EventEnd = self.clock + sys.maxsize
            Truck.TimeBetweenQueue = self.clock
        else:
            self.Loading(Truck)

    def Loading(self, Truck):
        Truck.Event = 4
        # Truck.duration = 5
        Truck.duration = self.gera_tempo_carga(Truck.Loader, Truck.Fleet)
        Truck.EventEnd = self.clock + Truck.duration
        Truck.NextEvent = Truck.Event + 1
        Truck.autonomy = Truck.autonomy - Truck.duration / 60
        self.d_LoadResource[Truck.Loader].loading = 1
        self.write_file("\TruckEvents"+str(self.RepNumber)+".txt", Truck.Fleet, Truck.index, Truck.Event, Truck.Loader, Truck.duration)
        self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (
                self.s_md_times['Day'] == int(self.clock // 1440))] += Truck.duration

    def LoadedHaulage(self, Truck):
        if len(self.d_LoadResource[Truck.Loader].queue) > 0:
            Truck_index = self.d_LoadResource[Truck.Loader].queue[0]
            self.d_LoadResource[Truck.Loader].queue.pop(0)
            Truck_fora_queue = self.d_TruckResource[Truck_index]
            Truck_fora_queue.duration = self.clock - Truck_fora_queue.TimeBetweenQueue
            self.write_file("\TruckEvents"+str(self.RepNumber)+".txt", Truck_fora_queue.Fleet, Truck_fora_queue.index, Truck_fora_queue.Event, Truck_fora_queue.Loader, Truck_fora_queue.duration)
            self.s_md_times[Truck_fora_queue.Event].loc[(self.s_md_times['Fleet'] == Truck_fora_queue.Fleet) & (self.s_md_times['Day'] == int(self.clock//1440))]+= Truck_fora_queue.duration
            self.Loading(Truck_fora_queue)
            self.d_LoadResource[Truck.Loader].QueueAverNumber += 1
            self.d_LoadResource[Truck.Loader].QueueAverTime += Truck_fora_queue.duration
        else:
            self.d_LoadResource[Truck.Loader].loading = 0
        self.d_LoadResource[Truck.Loader].InRoute -= 1
        Truck.Event = 5
        Truck.duration = self.gera_tempo_viagem_cheio(Truck.Fleet, Truck.origem, Truck.Discharge)
        Truck.EventEnd = self.clock + Truck.duration
        Truck.NextEvent = 6
        Truck.autonomy = Truck.autonomy - Truck.duration / 60
        self.write_file("\TruckEvents"+str(self.RepNumber)+".txt", Truck.Fleet, Truck.index, Truck.Event, Truck.Loader, Truck.duration)
        self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (
                self.s_md_times['Day'] == int(self.clock // 1440))] += Truck.duration

    def DischargeQueue(self, Truck):
        if (self.d_DiscResource[Truck.Discharge].Type == 1) and (len(self.d_DiscResource[Truck.Discharge].queue) > 0 or self.d_DiscResource[Truck.Discharge].Unloading == 1):
            self.d_DiscResource[Truck.Discharge].queue.append(Truck.index)
            Truck.Event = 6
            Truck.EventEnd = self.clock + 1000000
            Truck.TimeBetweenQueue_Disc = self.clock
        else:
            self.Unloading(Truck)

    def Unloading(self, Truck):
        Truck.Event = 7
        duration = self.gera_tempo_basculo(Truck.Fleet, Truck.Discharge)
        Discharge = self.d_DiscResource[Truck.Discharge]
        Discharge.Unloading = 1
        Truck.duration = max(0,duration)
        if Discharge.HasPile == 1:
            Truck.duration = max(duration,
                              ((Discharge.DischargeMass/Discharge.produt)*60 - (self.clock - Discharge.UnloadingTime)))

        Truck.EventEnd = self.clock + Truck.duration
        Truck.NextEvent = 8
        self.write_file("\TruckEvents"+str(self.RepNumber)+".txt", Truck.Fleet, Truck.index, Truck.Event, Truck.Discharge, Truck.duration)
        self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (
                    self.s_md_times['Day'] == int(self.clock // 1440))] += Truck.duration

        # SE FOR A PRIMEIRA PILHA
        Discharge.UnloadingTime = self.clock
        Discharge.DischargeMass = Truck.Capacity
        #aux = self.d_DiscResource[Truck.Discharge].DischargeMass / (self.clock - self.d_DiscResource[Truck.Discharge].UnloadingTime)
        if Discharge.Type == 1:
            Pile = self.d_Piles[Discharge.Pile]
            self.OreMass += Truck.Capacity
            self.d_Plants[Discharge.Plant].YardMass = self.d_Plants[Discharge.Plant].YardMass + Truck.Capacity
            if int(self.clock // 1440) not in self.s_d_massas.keys():
                self.s_d_massas[int(self.clock // 1440)] = [Truck.Capacity,0]
            else:
                self.s_d_massas[int(self.clock // 1440)][0] = Truck.Capacity + self.s_d_massas[int(self.clock // 1440)][0]
        elif Discharge.Type == 3:
            self.WasteMass += Truck.Capacity
            if int(self.clock // 1440) not in self.s_d_massas.keys():
                self.s_d_massas[int(self.clock // 1440)] = [0,Truck.Capacity]
            else:
                self.s_d_massas[int(self.clock // 1440)][1] = Truck.Capacity + self.s_d_massas[int(self.clock // 1440)][1]
        else:
            self.OreMass += Truck.Capacity
        if (self.OreMass + self.WasteMass) > Truck.Capacity:
            self.TripsFile = open(self.OutputPath + "\Trips"+ str(self.RepNumber) + ".txt", 'a')
            self.TripsFile.write(
                "{:.2f}".format(self.clock / 1440) + "," + str(Truck.Front) + "," + str(Truck.Material) + "," + str(
                    Truck.Discharge) + "," + str(Truck.Capacity) + '\n')
            self.TripsFile.close()
        else:
            self.TripsFile.write(
                Truck.Fleet + ',Truck_'+ str(self.clock / 1440) + "," + str(Truck.Front) + "," + str(Truck.Material) + "," + str(
                    Truck.Discharge) + "," + str(Truck.Capacity) + '\n')
            self.TripsFile.close()

        # ATUALIZA DESCARGA
        if Discharge.Type == 1:
            for i in self.d_WeightGrades.keys():
                if Pile.massa == 0:
                    Pile.inicio = self.clock
                    Pile.quality[i] = Truck.quality[i][0]
                    if self.d_WeightGrades[i] not in self.d_WeightGrades.keys():
                        Pile.quality[self.d_WeightGrades[i]] = Truck.quality[i][1]
                else:
                    if self.d_WeightGrades[i] == 'Global':
                        Pile.quality[i] = (Pile.quality[i] * Pile.massa + Truck.quality[i][0] * Truck.Capacity) \
                                             / (Pile.massa + Truck.Capacity)
                    else:
                        Pile.quality[i] = (Pile.quality[i] * Pile.quality[
                            self.d_WeightGrades[i]] * Pile.massa + Truck.quality[i][0] * Truck.quality[i][
                                                  1] * Truck.Capacity) \
                                             / (Pile.quality[self.d_WeightGrades[i]] * Pile.massa +
                                                Truck.quality[i][1] * Truck.Capacity)
                        if self.d_WeightGrades[i] not in self.d_WeightGrades.keys():
                            Pile.quality[self.d_WeightGrades[i]] = (Pile.quality[
                                                                              self.d_WeightGrades[i]] * Pile.massa + \
                                                                          Truck.quality[i][1] * Truck.Capacity) / (
                                                                                 Pile.massa + Truck.Capacity)

            Pile.massa += Truck.Capacity
            if Pile.massa >= Pile.Capacity and Discharge.Type == 1:
                self.optimize = 1
                Plant = self.d_Plants[Discharge.Plant]
                Pile.Rate = Plant.Rate
                print("Rate == ", Plant.Rate)
                #'''
                if Discharge.HasPile == 1:
                    aux = 1
                    for i in self.d_LowerBoundSize.keys():
                        if Discharge.id == i[0] and Pile.quality[i[1]] > self.d_LowerBoundSize[i]:
                            if aux != 1 and aux > self.d_LowerBoundSize[i]/Pile.quality[i[1]]:
                                aux = self.d_LowerBoundSize[i]/Pile.quality[i[1]]
                            else:
                                aux = self.d_LowerBoundSize[i]/Pile.quality[i[1]]
                        Pile.Rate = Plant.Rate*aux
                # ENCERRAR Pile ATUAL
                Discharge.d_PileStatus["Stacking"] = 0
                if Discharge.d_PileStatus["Reclaiming"] == 0:
                    if len(Discharge.WaitingPiles) > 0:
                        Pile.Reclaiming = 0
                        Pile.Stacking = 0
                        Pile.Waiting = 1
                        Discharge.WaitingPiles.append(Pile.index)
                        self.d_Piles[Discharge.WaitingPiles[0]].Reclaiming = 1
                        self.d_Piles[Discharge.WaitingPiles[0]].Stacking = 0
                        self.d_Piles[Discharge.WaitingPiles[0]].Waiting = 0
                        Discharge.d_PileStatus["Reclaiming"] = Discharge.WaitingPiles[0]
                        del Discharge.WaitingPiles[0]
                    else:
                        Pile.Reclaiming = 1
                        Pile.Stacking = 0
                        Pile.Waiting = 0
                        Discharge.d_PileStatus["Reclaiming"] = Pile.index
                #TERMINOU DE FORMAR A PILHA ATUAL, MAS TEM OUTRA PILHA SENDO RETOMADA
                elif self.d_Piles[Discharge.d_PileStatus["Reclaiming"]].massa > 0:
                    Pile.Reclaiming = 0
                    Pile.Stacking = 0
                    Pile.Waiting = 1
                    Discharge.WaitingPiles.append(Pile.index)
                #TERMINOU DE FORMAR A PILHA ATUAL E N O TEM NENHUMA PILHA SENDO RETOMADA
                elif self.d_Piles[Discharge.d_PileStatus["Reclaiming"]].massa <= 0:
                    if len(Discharge.WaitingPiles) > 0:
                        Pile.Reclaiming = 0
                        Pile.Stacking = 0
                        Pile.Waiting = 1
                        Discharge.d_PileStatus["Reclaiming"] = Discharge.WaitingPiles[0]
                        Discharge.WaitingPiles.append(Pile.index)
                        del Discharge.WaitingPiles[0]
                        self.d_Piles[Discharge.WaitingPiles[0]].Reclaiming = 1
                        self.d_Piles[Discharge.WaitingPiles[0]].Stacking = 0
                        self.d_Piles[Discharge.WaitingPiles[0]].Waiting = 0
                    else:
                        Pile.Reclaiming = 1
                        Pile.Stacking = 0
                        Pile.Waiting = 0
                        Discharge.d_PileStatus["Reclaiming"] = Pile.index
                self.PileFile = open(self.OutputPath + "\OrePiles"+ str(self.RepNumber) + ".txt", 'a')
                if Pile.index == 1:
                    self.PileFile.write(" Index,Discharge,Mass,")
                    for i in Pile.quality.keys():
                        self.PileFile.write(i + ',')
                    self.PileFile.write('Ratio,Time,Start ,\n')

                self.PileFile.write(str(Pile.index) + "," + str(Pile.Discharge) + "," + str(Pile.massa) + ",")
                for i in Pile.quality.keys():
                    self.PileFile.write(str(round(Pile.quality[i], 2)) + ',')
                self.PileFile.write(str(Pile.Rate) + ',' + "{:.0f}".format(self.clock) + ',')
                self.PileFile.write("{:.0f}".format(Pile.inicio) + ',')
                self.PileFile.write('\n')
                self.PileFile.close()
                # FIM ENCERRAR PILHA ATUAL

                # GERAR NOVA Pile
                self.PileIndex += 1
                self.d_Piles[self.PileIndex] = self.Piles(self.PileIndex, Discharge.id, Discharge.BatchMass, 0,
                                                                0, 1)
                Discharge.d_PileStatus["Stacking"] = self.PileIndex
                Discharge.Pile = self.PileIndex
                Pile = self.d_Piles[self.PileIndex]
                for i in self.d_WeightGrades.keys():
                    Pile.quality[i] = 0
                    if self.d_WeightGrades[i] not in self.d_WeightGrades.keys():
                        Pile.quality[self.d_WeightGrades[i]] = 0
                Pile.Reclaiming = 0
                Pile.Stacking = 1
                Pile.Waiting = 0

    def TruckMaintenance(self, Truck):
        if Truck.Event == 7:
            if len(self.d_DiscResource[Truck.Discharge].queue) > 0:
                Truck_index = self.d_DiscResource[Truck.Discharge].queue[0]
                self.d_DiscResource[Truck.Discharge].queue.pop(0)
                Truck_fora_queue = self.d_TruckResource[Truck_index]
                Truck_fora_queue.duration = self.clock - Truck_fora_queue.TimeBetweenQueue_Disc
                self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                self.TrucksEventFile.write(
                    Truck_fora_queue.Fleet + ',Truck_' + str(Truck_fora_queue.index) + "," + str(Truck_fora_queue.Event) + "," + "{:.2f}".format(
                        self.clock - Truck_fora_queue.duration) + "," + Truck_fora_queue.Discharge + "," + str("{:.2f}".format(Truck_fora_queue.duration)) + '\n')
                self.TrucksEventFile.close()
                self.s_md_times[Truck_fora_queue.Event].loc[(self.s_md_times['Fleet'] == Truck_fora_queue.Fleet) & (
                            self.s_md_times['Day'] == int(self.clock // 1440))] += Truck_fora_queue.duration

                self.Unloading(Truck_fora_queue)
            else:
                self.d_DiscResource[Truck.Discharge].Unloading = 0
        if self.clock > Truck.MainFinalEvent_Truck:
            Truck.Event = 8
            Truck.duration = self.gera_num_aleatorio(self.df_MainDurTime_truck.loc[Truck.Fleet]['Expressao'], \
                                                  self.df_MainDurTime_truck.loc[Truck.Fleet]['Param_1'],
                                                  self.df_MainDurTime_truck.loc[Truck.Fleet]['Param_2'], \
                                                  self.df_MainDurTime_truck.loc[Truck.Fleet]['Param_3'])

            Truck.MainFinalEvent_Truck = self.clock + self.gera_num_aleatorio(
                self.df_MainBetTime_truck.loc[Truck.Fleet]['Expressao'], \
                self.df_MainBetTime_truck.loc[Truck.Fleet]['Param_1'],
                self.df_MainBetTime_truck.loc[Truck.Fleet]['Param_2'], \
                self.df_MainBetTime_truck.loc[Truck.Fleet]['Param_3'])

            Truck.NextEvent = 9
            Truck.EventEnd = self.clock + Truck.duration
            self.write_file("\TruckEvents"+str(self.RepNumber)+".txt", Truck.Fleet, Truck.index, 8, '', Truck.duration)
            self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (self.s_md_times['Day'] == int(self.clock//1440))]+= Truck.duration
        else:
            self.ShiftTurn(Truck)

    def ShiftTurn(self, equipamento):
        if not self.df_ShiftTurn.empty:
            tempo_horas = (self.clock % 1440) / 60
            existe = []
            if equipamento.Type == "Caminhão":
                existe = self.df_ShiftTurn[
                    (tempo_horas >= self.df_ShiftTurn['Start']) & (tempo_horas < self.df_ShiftTurn['End']) & (
                                self.df_ShiftTurn["Equipamento"] == "Caminhões")]
                if len(existe) > 0:
                    equipamento.Event = 9
                    equipamento.duration = float(
                        self.df_ShiftTurn['Duracao'][(self.df_ShiftTurn['Equipamento'] == "Caminhões")].iloc[0])
                    equipamento.EventEnd = self.clock + equipamento.duration
                    equipamento.NextEvent = 10
                    self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                    self.TrucksEventFile.write(
                        equipamento.Fleet + ',Truck_'+ str(equipamento.index) + "," + "9" + "," + "{:.2f}".format(self.clock) + "," + " ,"+ str("{:.2f}".format(equipamento.duration)) + '\n')
                    self.TrucksEventFile.close()
                    self.s_md_times[equipamento.Event].loc[(self.s_md_times['Fleet'] == equipamento.Fleet) & (
                            self.s_md_times['Day'] == int(self.clock // 1440))] += equipamento.duration

                else:
                    self.FuelSupply(equipamento)
        else:
            self.FuelSupply(equipamento)

    def FuelSupply(self, Truck):
        if not self.df_Refueling.empty:
            if Truck.autonomy <= 0.5:
                Truck.Event = 10
                Truck.autonomy = self.df_Refueling['Autonomy'][(self.df_Refueling['ID'] == Truck.Fleet)].iloc[0]
                Truck.duration = self.df_Refueling['Time'][(self.df_Refueling['ID'] == Truck.Fleet)].iloc[0]
                Truck.duration = Truck.duration * 60
                self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                self.TrucksEventFile.write(
                    Truck.Fleet + ',Truck_'+ str(Truck.index) + "," + str(Truck.Event) + "," + "{:.2f}".format(self.clock) + "," + str("{:.2f}".format(Truck.duration)) + '\n')
                Truck.EventEnd = self.clock + Truck.duration
                Truck.NextEvent = 11
                self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (self.s_md_times['Day'] == int(self.clock//1440))]+= Truck.duration
            else:
                self.OtherEvents(Truck)
        else:
            self.OtherEvents(Truck)

    def OtherEvents(self, Truck):
        aux = min(Truck.d_RandomFinalEvent_Truck.values())

        if aux >= 0:
            if self.clock > aux:
                for i in Truck.d_RandomFinalEvent_Truck.keys():
                    if Truck.d_RandomFinalEvent_Truck[i] == aux:
                        aux = i

                Truck.duration = self.gera_num_aleatorio(self.d_durac_eventos_aleatorios_cam[aux]['Expressao'], \
                                                      self.d_durac_eventos_aleatorios_cam[aux]['Param_1'],
                                                      self.d_durac_eventos_aleatorios_cam[aux]['Param_2'], \
                                                      self.d_durac_eventos_aleatorios_cam[aux]['Param_3'])
                Truck.d_RandomFinalEvent_Truck[aux] = self.clock + self.gera_num_aleatorio(self.d_entre_eventos_aleatorios_cam[aux]['Expressao'], \
                                                      self.d_entre_eventos_aleatorios_cam[aux]['Param_1'],
                                                      self.d_entre_eventos_aleatorios_cam[aux]['Param_2'], \
                                                      self.d_entre_eventos_aleatorios_cam[aux]['Param_3'])
                aux2 = Truck.d_RandomFinalEvent_Truck[aux]
                Truck.Event = 11
                Truck.NextEvent = 1
                Truck.EventEnd = self.clock + Truck.duration
                self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                self.TrucksEventFile.write(
                    Truck.Fleet + ',Truck_'+ str(Truck.index) + "," + str(Truck.Event) + "," + "{:.2f}".format(self.clock) +","+ aux + "," + str("{:.2f}".format(Truck.duration)) + '\n')
                self.TrucksEventFile.close()
                self.s_md_times[Truck.Event].loc[(self.s_md_times['Fleet'] == Truck.Fleet) & (self.s_md_times['Day'] == int(self.clock//1440))]+= Truck.duration
            else:
                self.EmptyHaulage(Truck)
        else:
            self.EmptyHaulage(Truck)

    #Loading equipment functions
    def LoaderOtherEvents(self, esc):
        aux = min(esc.d_EventEnd_alea_esc.values())
        if aux > 0:
            if self.clock > aux:
                for i in esc.d_EventEnd_alea_esc.keys():
                    if esc.d_EventEnd_alea_esc[i] == aux:
                        aux = i
                esc.disp = 0
                esc.duration = self.gera_num_aleatorio(self.d_durac_eventos_aleatorios_esc[aux]['Expressao'], \
                                                      self.d_durac_eventos_aleatorios_esc[aux]['Param_1'],
                                                      self.d_durac_eventos_aleatorios_esc[aux]['Param_2'], \
                                                      self.d_durac_eventos_aleatorios_esc[aux]['Param_3'])
                esc.d_EventEnd_alea_esc[aux] = self.clock + self.gera_num_aleatorio(self.d_entre_eventos_aleatorios_esc[aux]['Expressao'], \
                                                      self.d_entre_eventos_aleatorios_esc[aux]['Param_1'],
                                                      self.d_entre_eventos_aleatorios_esc[aux]['Param_2'], \
                                                      self.d_entre_eventos_aleatorios_esc[aux]['Param_3'])
                aux2 = esc.d_EventEnd_alea_esc[aux]
                esc.NextEvent = 1
                esc.EventEnd = self.clock + esc.duration
                self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'a')
                self.LoaderEventFile.write(
                    str(esc.a_id) + "," + aux + "," + "{:.2f}".format(self.clock) + "," + str(esc.duration) + '\n')
                self.LoaderEventFile.close()
            else:
                self.LoaderMaintenance(esc)
        else:
            self.LoaderMaintenance(esc)

    def LoaderWorking(self, obj_escavadeira):
        obj_escavadeira.disp = 1
        if obj_escavadeira.MainFinalEvent_Loader >= self.clock and obj_escavadeira.autonomy > 0.5 and obj_escavadeira.t_movement== 0:
            obj_escavadeira.duration = 10
            obj_escavadeira.NextEvent = 7
            obj_escavadeira.EventEnd = self.clock + obj_escavadeira.duration
            self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'a')
            self.LoaderEventFile.write(
                str(obj_escavadeira.a_id) + "," + "Working" + "," + "{:.2f}".format(self.clock) + "," + str(
                    obj_escavadeira.EventDuration) + '\n')
            self.LoaderEventFile.close()
        else:
            self.LoaderOtherEvents(obj_escavadeira)

    def LoaderMovement(self,obj_escavadeira):
        if obj_escavadeira.t_movement >0:
            obj_escavadeira.disp = 0
            obj_escavadeira.duration = obj_escavadeira.t_movement
            self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'a')
            self.LoaderEventFile.write(
                str(obj_escavadeira.a_id) + "," + "Deslocando" + "," + "{:.2f}".format(self.clock) + "," + str(
                    obj_escavadeira.EventDuration) + '\n')
            self.LoaderEventFile.close()
            obj_escavadeira.NextEvent = 4
            obj_escavadeira.EventEnd = self.clock + obj_escavadeira.duration
            obj_escavadeira.t_movement = 0
        else:
            self.LoaderShiftTurn(obj_escavadeira)

    def LoaderShiftTurn(self, obj_escavadeira):
        if not self.df_ShiftTurn.empty:
            tempo_horas = (self.clock % 1440) / 60
            existe = []
            existe = self.df_ShiftTurn[
                (tempo_horas >= self.df_ShiftTurn['Start']) & (tempo_horas < self.df_ShiftTurn['End']) & (
                            self.df_ShiftTurn['Equipamento'] == "Escavadeiras")]
            if len(existe) > 0:
                obj_escavadeira.Event = 4
                obj_escavadeira.duration = float(
                    self.df_ShiftTurn['Duracao'][(self.df_ShiftTurn['Equipamento'] == "Escavadeiras")].iloc[0])
                obj_escavadeira.EventEnd = self.clock + obj_escavadeira.duration
                obj_escavadeira.NextEvent = 5
                self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'a')
                self.LoaderEventFile.write(
                    str(obj_escavadeira.a_id) + "," + "Shift turn" + "," + "{:.2f}".format(self.clock) + "," + str(
                        obj_escavadeira.duration) + '\n')
                self.LoaderEventFile.close()
                obj_escavadeira.disp = 0
            else:
                self.NoAllocation(obj_escavadeira)
        else:
            self.NoAllocation(obj_escavadeira)

    def NoAllocation(self, obj_escavadeira):
        if self.TripsperLoader[obj_escavadeira.a_id] <1:
            obj_escavadeira.Event = 5
            obj_escavadeira.duration = self.OptimizationTime*60
            obj_escavadeira.EventEnd = self.clock + obj_escavadeira.duration
            obj_escavadeira.NextEvent = 6
            self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'a')
            self.LoaderEventFile.write(
                str(obj_escavadeira.a_id) + "," + "No allocated" + "," + "{:.2f}".format(self.clock) + "," + str(
                    obj_escavadeira.duration) + '\n')
            self.LoaderEventFile.close()
        else:
            self.LoaderWorking(obj_escavadeira)

    def LoaderFuelSupply(self, obj_escavadeira):
        # obj_escavadeira = self.d_LoadResource[ind_escavadeira]
        obj_escavadeira.disp = 1
        if obj_escavadeira.autonomy <= 0.5:
            obj_escavadeira.Event = 10

            '''
            obj_escavadeira.autonomy = self.df_Refueling['Autonomy'][(self.df_Refueling['ID'] == obj_escavadeira.Fleet)].iloc[0]
            obj_escavadeira.duration = self.df_Refueling['Tempo'][(self.df_Refueling['ID'] == obj_escavadeira.Fleet)].iloc[0]
            obj_escavadeira.duration = obj_escavadeira.duration*60
            self.TrucksEventFile = open("Eventos_obj_escavadeira.txt", 'a')
            self.arq_Events_obj_escavadeira.write(str(obj_escavadeira.index) + "," + "Abastecimento" + "," + "{:.2f}".format(self.clock) + "," + str(obj_escavadeira.duration) + '\n')
            obj_escavadeira.EventEnd = self.clock + obj_escavadeira.duration
            obj_escavadeira.NextEvent = 1
            '''
        else:
            self.LoaderMovement(obj_escavadeira)

    def LoaderMaintenance(self, obj_escavadeira):
            if self.clock < obj_escavadeira.MainFinalEvent_Loader and self.clock + 10 > obj_escavadeira.MainFinalEvent_Loader :
                obj_escavadeira.HasStop = 1
                self.LoaderFuelSupply(obj_escavadeira)
            elif self.clock > obj_escavadeira.MainFinalEvent_Loader:
                #if len(obj_escavadeira.queue) > 0 or obj_escavadeira.loading == 1 :
                if obj_escavadeira.InRoute > 0:
                    obj_escavadeira.MainFinalEvent_Loader += 10
                    self.LoaderFuelSupply(obj_escavadeira)
                else:
                    obj_escavadeira.disp = 0
                    obj_escavadeira.HasStop = 0
                    obj_escavadeira.MainEventDuration_Loader = self.gera_num_aleatorio(
                        self.df_MainDurTime_loader.loc[obj_escavadeira.a_id]['Expressao'], \
                        self.df_MainDurTime_loader.loc[obj_escavadeira.a_id]['Param_1'],
                        self.df_MainDurTime_loader.loc[obj_escavadeira.a_id]['Param_2'], \
                        self.df_MainDurTime_loader.loc[obj_escavadeira.a_id]['Param_3'])
                    obj_escavadeira.MainFinalEvent_Loader = 0
                    while obj_escavadeira.MainFinalEvent_Loader < (obj_escavadeira.MainEventDuration_Loader + self.clock):
                        obj_escavadeira.MainFinalEvent_Loader = self.clock + self.gera_num_aleatorio(
                            self.df_MainBetTime_loader.loc[obj_escavadeira.a_id]['Expressao'], \
                            self.df_MainBetTime_loader.loc[obj_escavadeira.a_id]['Param_1'],
                            self.df_MainBetTime_loader.loc[obj_escavadeira.a_id]['Param_2'], \
                            self.df_MainBetTime_loader.loc[obj_escavadeira.a_id]['Param_3'])

                    self.LoaderEventFile = open(self.OutputPath + "\Eventos_esc"+ str(self.RepNumber) + ".txt", 'a')
                    self.LoaderEventFile.write(
                        str(obj_escavadeira.a_id) + "," + "Maintenance" + "," + "{:.2f}".format(self.clock) + "," + str(
                            obj_escavadeira.EventDuration) + '\n')
                    self.LoaderEventFile.close()
                    obj_escavadeira.NextMainEvent_Loader = 1
                    obj_escavadeira.NextEvent = 2
                    obj_escavadeira.EventEnd = self.clock + obj_escavadeira.MainEventDuration_Loader
                    if obj_escavadeira.MainEventDuration_Loader >= self.OptimizationTime * 60:
                        print(" Call the MILP solve due the loading machine long breakdown ", obj_escavadeira.a_id)
                        self.optimize = 1
            else:
                self.LoaderFuelSupply(obj_escavadeira)

    #Plant's functions
    def inicia_usinas(self, m_df_Plant):
        for i in list(m_df_Plant.index):
            aux_list = []
            aux_list = list(m_df_Plant.loc[i])
            self.d_Plants[i] = self.Usina(aux_list[0], aux_list[1], aux_list[2], aux_list[3])
            self.d_Plants[i].index = aux_list[0]
            self.d_Plants[i].status = 0
            for j in self.d_DiscResource.keys():
                if self.d_Plants[i].Discharge == j:
                    self.d_DiscResource[j].Plant = i
            self.EquipmentList.append(self.d_Plants[i])
            self.d_Plants[i].duration = 10
            self.d_Plants[i].Event = 101
            self.d_Plants[i].EventEnd = self.clock + self.d_Plants[i].duration
            self.d_Plants[i].NextEvent = 101
            self.PlantMaintenance(self.d_Plants[i])

    def Reclaim_Pile(self, check_retomada):
        Erase = 0
        for i in self.d_Piles.keys():
            Discharge = self.d_Piles[i].Discharge
            Plant = self.d_DiscResource[Discharge].Plant
            if self.d_Plants[Plant].status == 1:
                if self.d_Piles[i].Reclaiming == 1:
                    if self.d_Piles[i].massa > 0:
                        self.d_Piles[i].massa = self.d_Piles[i].massa - self.d_Piles[i].Rate * (10 / 60)
                        self.d_Plants[Plant].YardMass = self.d_Plants[Plant].YardMass - self.d_Piles[i].Rate * (
                                    10 / 60)
                        #print("Pilha = ", i)
                        #print("Massa retomada = ", self.d_Piles[i].Rate * (10 / 60), ". Taxa = ", self.d_Piles[i].Rate )

                        self.FeedMass = self.FeedMass + self.d_Piles[i].Rate * (10 / 60)
                    else:
                        self.d_Piles[i].Reclaiming = 0
                        self.d_DiscResource[Discharge].d_PileStatus["Reclaiming"] = 0
                        if self.d_DiscResource[Discharge].HasPile == 1:
                            print("Pile", i, "completely formed")
                        Erase = i
                if self.d_Piles[i].Waiting == 1:
                    #if self.d_DiscResource[Discharge].d_PileStatus["Reclaiming"] == 0:
                    if self.d_DiscResource[Discharge].d_PileStatus["Reclaiming"] == 0:
                        print("Ore pile = ", self.d_Piles[i].index)
                        print(len(self.d_DiscResource[Discharge].WaitingPiles))
                        print("Discharge = ", self.d_DiscResource[Discharge].index)
                        del self.d_DiscResource[Discharge].WaitingPiles[0]
                        self.d_DiscResource[Discharge].d_PileStatus["Reclaiming"] = i
                        self.d_DiscResource[Discharge].d_PileStatus["Aguardando"] = 0
                        self.d_Piles[i].Reclaiming = 1
                        self.d_Piles[i].Waiting = 0
                        if self.d_DiscResource[Discharge].Pile == 1:
                            print("Ore pile", i, "starting to be reclaimed")
                            print("Reclaiming -> Discharge  ", Discharge, "-> Pile",
                                  self.d_DiscResource[Discharge].d_PileStatus["Reclaiming"],
                                  "  = ", self.d_Piles[self.d_DiscResource[Discharge].d_PileStatus["Reclaiming"]].massa,
                                  'Time = ', self.clock)
                        self.d_Piles[i].massa = self.d_Piles[i].massa - self.d_Piles[i].Rate * (10 / 60)
                        self.d_Plants[Plant].YardMass = self.d_Plants[Plant].YardMass - self.d_Piles[i].Rate * (
                                    10 / 60)
                        self.FeedMass = self.FeedMass + self.d_Piles[i].Rate * (10 / 60)
                        self.optimize = 1
            check_retomada.duration = 10
            check_retomada.Event = 101
            check_retomada.EventEnd = self.clock + check_retomada.duration
            check_retomada.NextEvent = 101

        if Erase > 0:
            del self.d_Piles[Erase]

    def PlantMaintenance(self, Plant):
        if not self.df_MainDurTime_plant.empty:
                if Plant.status == 1:
                    Plant.duration_man = self.gera_num_aleatorio(self.df_MainDurTime_plant.loc[Plant.index]["Expressao"], \
                                                                self.df_MainDurTime_plant.loc[Plant.index]["Param_1"],
                                                                self.df_MainDurTime_plant.loc[Plant.index]["Param_2"], \
                                                                self.df_MainDurTime_plant.loc[Plant.index]["Param_3"])
                    #Plant.Event_man = 102
                    Plant.EventEnd = self.clock + Plant.duration_man
                    Plant.NextEvent = 102
                    Plant.status = 0
                    self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                    self.TrucksEventFile.write(
                        Plant.index + "," + "inicio_parada" + "," + "{:.2f}".format(self.clock) + "," + str(
                            Plant.duration_man) + '\n')
                    self.TrucksEventFile.close()
                else:
                    Plant.status = 1
                    Plant.duration_man = self.gera_num_aleatorio(self.df_MainBetTime_plant.loc[Plant.index]["Expressao"], \
                                                                self.df_MainBetTime_plant.loc[Plant.index]["Param_1"],
                                                                self.df_MainBetTime_plant.loc[Plant.index]["Param_2"], \
                                                                self.df_MainBetTime_plant.loc[Plant.index]["Param_3"])
                    Plant.prox_man = self.clock + Plant.duration_man
                    Plant.EventEnd = self.clock + Plant.duration_man
                    Plant.NextEvent = 102
                    self.TrucksEventFile = open(self.OutputPath + "\TruckEvents"+ str(self.RepNumber) + ".txt", 'a')
                    self.TrucksEventFile.write(
                        Plant.index + "," + "End_Stop" + "," + "{:.2f}".format(self.clock) + "," + str(
                            Plant.EventEnd) + '\n')
                    self.TrucksEventFile.close()
        else:
            #
            Plant.status = 1
            Plant.EventEnd = float('inf')
            Plant.NextEvent = 102

    #Advance simulation clock
    def avanca_relogio(self):
        Times = [i.EventEnd for i in self.EquipmentList]
        t_Event = 0
        t_Event = min(Times)
        index = 0
        index = Times.index(t_Event)
        self.clock = t_Event
        texto = self.EquipmentList[index].Events[self.EquipmentList[index].NextEvent]
        exec("self." + texto + "(self.EquipmentList[index])")