from gurobipy import *

def solve(M, df_Truck, df_LoadingMachine, \
          df_Discharge, d_LowerBoundGrade, d_UpperBoundGrade, \
          d_LowerBoundSize, d_UpperBoundSize, o_d_regions, F, d_WeightGrades, lito, v_WasteName, massa, \
          SD, WT, o_d_PileMasses, o_d_PileQualities, NM,CT,m_PlantTime, \
          df_MovTime_loader, d_LastAlocation,d_MinMaxGrades,d_MinMaxSizes,status,o_d_RegionsRatio, TPM,o_l_PrioritizationOrder,\
          df_LocalComp, o_l_weight,v_tolerance):

    l_aux = []
    for i in o_d_RegionsRatio.keys():
        if o_d_RegionsRatio[i][2] > 0.99 * o_d_RegionsRatio[i][1]:
            l_aux.append(i)
    if len(l_aux) > 0:
        for i in l_aux:
            del(o_d_RegionsRatio[i])
    GDW_n = {}
    GDW_p = {}
    SDW_n = {}
    SDW_p = {}

    for i in d_MinMaxGrades.keys():
        if "Max" in d_MinMaxGrades[i]:
            GDW_n[i] = 10
            GDW_p[i] = 1
        else:
            GDW_n[i] = 1
            GDW_p[i] = 10

    for i in d_MinMaxSizes.keys():
        if d_MinMaxSizes[i] == "Max":
            SDW_n[i] = 100
            SDW_p[i] = 1

        else:
            SDW_n[i] = 1
            SDW_p[i] = 100


    d_LastAlocation2 = {}
    for i in d_LastAlocation.keys():
        d_LastAlocation2[i]  = d_LastAlocation[i]
    #to = 0
    dic_pesos = {}
    dic_pesos = d_WeightGrades
    m_d_LoadingMachine = {}
    aux = []
    aux = list(df_LoadingMachine.columns)

    for i in range(len(df_LoadingMachine)):
        m_d_LoadingMachine[df_LoadingMachine['ID'].iloc[i]] = list(df_LoadingMachine[aux[1:]].iloc[i])
    E, ER, e_v_WasteName, e_desloc, e_cava, EA, EMA, EOA = eval('multidict(m_d_LoadingMachine)')


    m_d_Trucks = {}
    aux = []
    aux = list(df_Truck.columns)
    for i in range(len(df_Truck)):
        m_d_Trucks[df_Truck['ID'].iloc[i]] = list(df_Truck[aux[1:]].iloc[i])
    T, N, TC, CTT, TMA, TOA = eval('multidict(m_d_Trucks)')

    TDE = {}
    for i in df_MovTime_loader.index:
        aux = eval(i)
        TDE[aux] = int(df_MovTime_loader['Tempo'].loc[i])


    m_d_descarga = {}
    aux = []
    aux = list(df_Discharge.columns)
    for i in range(len(df_Discharge)):
        m_d_descarga[df_Discharge['ID'].iloc[i]] = list(df_Discharge[aux[1:]].iloc[i])
    D, DR, d_cava, DT, d_max_fila, d_simul, d_tamanho, d_prior, DS,d_mlc = eval('multidict(m_d_descarga)')
    cont = 0

    G = []
    for i in d_UpperBoundGrade.keys():
        if i[1] not in G:
            G.append(i[1])

    S = []
    for i in d_UpperBoundSize.keys():
        if i[1] not in S:
            S.append(i[1])
    # -----------------------------------------------------
    dic_materials = {}

    for i in [*o_d_regions]:
        if (o_d_regions[i][lito] in v_WasteName):
            e_Ore = 0
        else:
            e_Ore = 1

        dic_materials.update({i: [o_d_regions[i][massa], e_Ore, o_d_regions[i]['Order_'], \
                                  o_d_regions[i]['Independent_'], o_d_regions[i]['MMU_']]})

    materiais, MM, MT, ordem, FR, uml = multidict(dic_materials)
    cont = 0

    # -----------------------------------------------------
    dic_elements = {}
    for i in dic_materials.keys():
        for k in G:
            lista = []
            lista.append(o_d_regions[i][k])
            lista.append(o_d_regions[i][dic_pesos[k]])
            dic_elements.update({(i[0], i[1], k): lista})

    teores, GM, SP = eval('multidict(dic_elements)')
    cont = 0


    # PILHAS

    pilha, MP = multidict(o_d_PileMasses)

    dic_PilesElements = {}

    for i in o_d_PileQualities.keys():
        for k in G:
            if k == i[1]:
                lista = []
                lista.append(o_d_PileQualities[i])
                if dic_pesos[i[1]] == 'Global':
                    cont +=1
                    lista.append(100)
                else:
                    lista.append(o_d_PileQualities[(i[0],dic_pesos[i[1]])])
                    cont +=1
                dic_PilesElements.update({i: lista})

    teores_pilha, GP, SPP = multidict(dic_PilesElements)


    dic_ParticleSize = {}
    lista = []
    for i in dic_materials.keys():
        for k in S:
            lista = []
            lista.append(o_d_regions[i][k])
            dic_ParticleSize.update({(i[0], i[1], k): lista})


    granuls, SM = multidict(dic_ParticleSize)

    dic_PilesParticleSize = {}
    lista = []
    for i in o_d_PileQualities.keys():
        for k in S:
            if k == i[1]:
                lista = []
                lista.append(o_d_PileQualities[i])
                cont+=1
                dic_PilesParticleSize.update({i: lista})
    granuls_pilha, SPS = multidict(dic_PilesParticleSize)




    # ---------------------------------------------------------
    cont = 0
    dic_meta_teor = {}
    i = list(d_LowerBoundGrade.keys())
    j = list(d_UpperBoundGrade.keys())
    for cont in range(len(i)):
        dic_meta_teor.update(
            {i[cont]: [float(d_LowerBoundGrade[i[cont]]), float(d_UpperBoundGrade[i[cont]])]})

    teor, GT_n, GT_p = eval('multidict(dic_meta_teor)')


    cont = 0
    dic_meta_granulometria = {}
    i = list(d_LowerBoundSize.keys())
    j = list(d_UpperBoundSize.keys())
    for cont in range(len(i)):
        dic_meta_granulometria.update(
            {i[cont]: [float(d_LowerBoundSize[i[cont]]), float(d_UpperBoundSize[i[cont]])]})

    granul, ST_n, ST_p = eval('multidict(dic_meta_granulometria)')
    #print(dic_meta_granulometria)


    R, RFM,RMP,RMA = multidict(o_d_RegionsRatio)


    P = [1]
    EB = {}
    if not df_LocalComp.empty:
        for e in E:
            for r in R:
                EB[(e, r)] = 1
    else:
        for e in E:
            for r in R:
                if e in df_LocalComp.index.values:
                    if r == df_LocalComp['Local'].loc[e] == r:
                        EB[(e,r)] = 1
                    else:
                        EB[(e,r)] = 0
                else:
                    EB[(e, r)] = 1

    # ===================== MILP MODEL MAIN BODY ============================================================
    m = Model("Produ  o")
    m.Params.LogToConsole = 0
    x = m.addVars(materiais, E, vtype=GRB.BINARY, name="x")
    w = m.addVars(D, F, M, T, lb=0, vtype=GRB.CONTINUOUS, name="w")
    dd_p = m.addVars(D, name="dd_p", lb = 0)
    dd_n = m.addVars(D, name="dd_n", lb = 0)
    gd_p = m.addVars(D, G, name="gd_p", lb = 0)
    gd_n = m.addVars(D, G, name="gd_n", lb = 0)
    sd_p = m.addVars(D, S, name="sd_p", lb = 0)
    sd_n = m.addVars(D, S, name="sd_n", lb = 0)
    srd = m.addVar(name="srd", lb = 0)
    un = m.addVars(D, F, M, T, name="un")
    drf_p= m.addVars(R,R, name = "drf_p", lb=0)
    drf_n = m.addVars(R, R, name="drf_n", lb=0)
    m.NumObj = 10
    m.setObjectiveN(sum(dd_p[k] + dd_n[k]*10 for k in D if DT[k] == 1 and d_prior[k] == 1), 0, priority= o_l_PrioritizationOrder[0], weight = o_l_weight[0])
    m.setObjectiveN(sum(gd_n[k, i]*GDW_n[k,i] + gd_p[k, i]*GDW_p[k,i]  for k in D if DT[k] == 1 and d_prior[k] == 1 for i in G if (k,i) in GDW_p.keys()), 1, priority=o_l_PrioritizationOrder[1], weight = o_l_weight[1])
    m.setObjectiveN(sum(sd_n[k, j]*SDW_n[k,j] + sd_p[k, j]*SDW_p[k,j] for k in D if DT[k] == 1 and d_prior[k] == 1 for j in S if (k,j) in SDW_p.keys()), 2, priority=o_l_PrioritizationOrder[2], weight = o_l_weight[2])
    m.setObjectiveN(sum(dd_p[k] + dd_n[k]*10 for k in D if DT[k] == 1 and d_prior[k] == 2), 3, priority=o_l_PrioritizationOrder[3], weight = o_l_weight[3])
    m.setObjectiveN(sum(gd_n[k, i]*GDW_n[k,i] + gd_p[k, i]*GDW_p[k,i]  for k in D if DT[k] == 1 and d_prior[k] == 2 for i in G if (k,i) in GDW_p.keys()), 4, priority= o_l_PrioritizationOrder[4], weight = o_l_weight[4])
    m.setObjectiveN(sum(sd_n[k, j]*SDW_n[k,j] + sd_p[k, j]*SDW_p[k,j] for k in D if DT[k] == 1 and d_prior[k] == 2 for j in S if (k,j) in SDW_p.keys()), 5, priority=o_l_PrioritizationOrder[5], weight = o_l_weight[5])
    m.setObjectiveN(srd, 6, priority=o_l_PrioritizationOrder[6], weight = o_l_weight[6])
    m.setObjectiveN(-1*sum(TC[t] * w[k, f, m, t]*(1 - MT[f, m]) for k in D for f in F for m in M if (f,m) in materiais for t in T ), 7, priority = o_l_PrioritizationOrder[7], weight = o_l_weight[7])
    m.setObjectiveN((drf_p.sum() + drf_n.sum()), 8, priority=o_l_PrioritizationOrder[8], weight = o_l_weight[8])
    m.setObjectiveN(w.sum(),9, priority=o_l_PrioritizationOrder[9], weight = o_l_weight[9])

    # MILP SET PARAMETERS
    m.Params.MIPGap = 0.05
    m.Params.Timelimit = 180

    # ESCAVATORS ASSIGNMENT CONSTRAINTS:
    Equation11_ = m.addConstrs((x.sum(f, m, "*") <= 1 for f in F for m in M), "Equation11_")
    Equation12_ = m.addConstrs((sum(x[f, m, e] / NM[f] for m in M for f in F if (f,m) in materiais) <= EA[e] for e in E), "Equation12_")
    Equation13_ = m.addConstrs( (x[f, m, e] - x[f, t, e] == 0 for f in F for m in M if (f, m) in materiais for t in M if ((f, t) in materiais and m!=t) for
         e in E), "Equation13")
    Equation14_ = m.addConstrs((x[f, m ,e] <= EB[e,FR[f,m]] for f in F for m in M if (f, m) in materiais and FR[f,m] in R for e in E), "Equation14_")
    Equation13_2 = m.addConstrs((x[f,m,e] + x[f1,m1,e1] <= 1 for f in F for m in M if (f, m) in materiais for f1 in F for m1 in M if (f1, m1) in materiais and (f,m) != (f1,m1) for e in E for e1 in E if e!=e1 and FR[f,m] == FR[f1,m1]), "Equation13_2")
    Equation13_3 = m.addConstrs((x[f,m,e] + x[f1,m1,e1] <= 1 for f in F for m in M if (f, m) in materiais for f1 in F for m1 in M if (f1, m1) in materiais for e in E for e1 in E if e==e1 and FR[f,m] != FR[f1,m1]), "Equation13_2")

    # MASS EXTRACTION CONSTRAINTS
    Equation15_ = m.addConstrs((sum(TC[t] * w[k, f, m, t] for t in T for k in D) <= MM[f, m] * x.sum(f, m, "*") for f in F \
                              for m in M if (f, m) in materiais), "Equation15_")
    Equation16_ = m.addConstrs((NM[f] * sum(TC[t] * w[k, f, m, t] for t in T for k in D for m in M) <= sum(x[f, m, e] * ER[e]*EMA[e]*EOA[e] * SD \
                for m in M if (f, m) in materiais for e in E if (d_LastAlocation[e] == 0 or FR[f,m] == d_LastAlocation[e])) + \
                sum(x[f, m, e] * ER[e] * EMA[e] * EOA[e] * (SD - (TDE[e, d_LastAlocation[e], FR[f, m]] / 60)) for m in M if (f, m) in materiais \
                    for e in E if  (d_LastAlocation[e] != 0 and FR[f, m] != d_LastAlocation[e])) for f in F),
                "Equation16_")

    # NUMBER OF TRIPS BETWEEN FRONTS AND DISCHARGES CONSTRAINTS:
    Equation17_ = m.addConstrs(
        (w[k, f, m, t] <= ((60 / CT[t,FR[f,m],k]) * un[k, f, m, t] * SD*TMA[t]*TOA[t]) for t in T for f in F for m in M for k in D if
         (f, m) in materiais), "Equation17_")
    Equation18_ = m.addConstrs((sum(un[k, f, m, t] for k in D for f in F for m in M) <= N[t] for t in T), "Equation18_")

    Equation19_= m.addConstrs((w[k, f, m, t] == 0 for f in F for m in M if (f,m) in materiais for t in T for k in D if (DT[k] != 3 and MT[f,m] == 0)), "Equation19_")

    Equation20_= m.addConstrs((w[k, f, m, t] == 0 for f in F for m in M if (f,m) in materiais for t in T for k in D if (DT[k] == 3 and MT[f,m] == 1)), "Equation20_")

    Equation20_1= m.addConstrs((w[k, f, m, t] == 0 for f in F for m in M if (f,m) in materiais for t in T for k in D if (DT[k] == 2 and m not in DEP_TIPOS[k])), "Equation20_1")

    # PLANTS CAPACITY
    Equation21_ = m.addConstrs((sum(
        TC[t] * w[k, f, m, t] * MT[f, m] for t in T for f in F for m in M if (f, m) in materiais) + dd_n[k] >=
                                 0.99*DR[k] * SD for k in D  if (DT[k] == 1)), "Equation21_")
    Equation22_ = m.addConstrs((sum(
        TC[t] * w[k, f, m, t] * MT[f, m]for t in T for f in F for m in M if (f, m) in materiais) - dd_p[k] <=\
            1.01 * DR[k] * SD for k in D if (DT[k] == 1)), "Equation22_")

    Equation23_ = m.addConstrs(
        (sum(GM[f, m, i] * sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] for f in F for m in M \
             if (f, m, i) in teores) + MP[k]*GP[k,i]*SPP[k,i] - gd_p[k, i] <= (1 + v_tolerance * 0.01) *GT_p[k, i] *(MP[k]*SPP[k,i] + sum(
            sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] \
            for f in F for m in M if (f, m, i) in teores)) for k in D if DT[k] == 1 and DS[k] == "s" for i in G if (k, i) in teor),
        "Equation23_")

    Equation24_ = m.addConstrs(
        (sum(GM[f, m, i]* sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] for f in F for m in M \
             if (f, m, i) in teores) + MP[k]*GP[k,i]*SPP[k,i] + gd_n[k, i] >= (1 - v_tolerance * 0.01) *GT_n[k, i] * (MP[k]*SPP[k,i] + sum(
            sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] \
            for f in F for m in M if (f, m, i) in teores)) for k in D if DT[k] == 1 and DS[k] == "s" for i in G if (k, i) in teor),
        "Equation24_")

    Equation23_1 = m.addConstrs(
        (sum(GM[f, m, i] * sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] for f in F for m in M \
             if (f, m, i) in teores) + MP[k]*GP[k,i]*SPP[k,i] - gd_p[k, i] <= GT_p[k, i] *(MP[k]*SPP[k,i] + sum(
            sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] \
            for f in F for m in M if (f, m, i) in teores)) for k in D if DT[k] == 1 and DS[k] == "n" for i in G if (k, i) in teor),
        "Equation23_1")

    Equation24_1 = m.addConstrs(
        (sum(GM[f, m, i]* sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] for f in F for m in M \
             if (f, m, i) in teores) + MP[k]*GP[k,i]*SPP[k,i] + gd_n[k, i] >= GT_n[k, i] * (MP[k]*SPP[k,i] + sum(
            sum(TC[t] * w[k, f, m, t] for t in T) * SP[f, m, i] \
            for f in F for m in M if (f, m, i) in teores)) for k in D if DT[k] == 1 and DS[k] == "n" for i in G if (k, i) in teor),
        "Equation24_2")

    Equation17 = m.addConstrs((gd_n[k, i] <= (GT_n[k,i]-GP[k,i])*MP[k]*SPP[k,i] for k in D if DT[k] == 1 and DS[k] == "n" for i in G if (k,i) in GDW_n.keys() and GDW_n[k,i] == 10 and GP[k,i] <= GT_n[k,i] ), "Equation17")
    Equation17_1 = m.addConstrs((gd_n[k, i] <= 0.1 for k in D if DT[k] == 1 and DS[k] == "n" for i in G if  (k,i) in GDW_n.keys() and GDW_n[k,i] == 10 and GP[k,i] > GT_n[k,i] ), "Equation17_1")



    # PARTICLE SIZE RANGE CONSTRAINTS:
    Equation18 = m.addConstrs((sum(SM[f, m, j] * sum(TC[t] * w[k, f, m, t] for t in T) for f in F for m in M \
                                   if (f, m, j) in granuls) + MP[k]*SPS[k,j] - sd_p[k, j] <= ST_p[k, j] *(MP[k] + sum(
        sum(TC[t] * w[k, f, m, t] for t in T) \
        for f in F for m in M if (f, m, j) in granuls)) for k in D if DT[k] == 1 for j in S if (k, j) in granul),
                              "Equation18")

    Equation19 = m.addConstrs((sum(SM[f, m, j] * MT[f, m] * sum(TC[t] * w[k, f, m, t] for t in T) for f in F for m in M \
                                   if (f, m, j) in granuls) + MP[k]*SPS[k,j] + sd_n[k, j] >= ST_n[k, j] *(MP[k] + sum(
        MT[f, m] * sum(TC[t] * w[k, f, m, t] for t in T) \
        for f in F for m in M if (f, m, j) in granuls) )for k in D if DT[k] == 1 for j in S if (k, j) in granul),
                              "Equation19")


    # STRIPPING RATIO CONSTRAINT:
    Equation19_1 = m.addConstr(SD * WT *2625 - srd == sum(
        (1 - MT[f, m]) * TC[t] * w[k, f, m, t] for t in T for f in F for m in M for k in D \
        if (f, m) in materiais), "Equation19_1")


    Equation20 = m.addConstrs(((sum(TC[t] * w[k, f, m, t] for t in T for k in D for f in F for m in M if (f, m) in materiais and FR[f, m] == r ) + RMA[r])/RMP[r] - \
                               (sum(TC[t] * w[k, f, m, t] for t in T for k in D for f in F for m in M if (f, m) in materiais and FR[f, m] == r_l) + RMA[r_l]) / RMP[r_l] == \
                               drf_p[r,r_l] - drf_n[r,r_l]  for r in R if r in R for r_l in R if r != r_l if r_l in R), "Equation20")


    m.optimize()
    dic_check_qualidade = {}
    dic_check_qualidade1 = {}
    for i in teor:
        dic_check_qualidade[i] = 0
        dic_check_qualidade1[i] = 0

    dic_check_granu = {}
    dic_check_granu1 = {}
    for i in granul:
        dic_check_granu[i] = 0
        dic_check_granu1[i] = 0
    dic_check_massa = {}
    for i in D:
        dic_check_massa[i] = 0
    dic_check_truck = {}
    for i in T:
        dic_check_truck[i] = 0
    dic_check_escav = {}
    for i in E:
        dic_check_escav[i] = 0
    print("NUMBER OF FOUND SOLUTIONS: ", m.SolCount)
    print("========================================")
    dic_alocacao = {}
    otimizar_teor = 0
    if m.SolCount > 0:
        status = 1
        for v in m.getVars():
            if "x[" in v.varName:
                if v.x > 0.5:
                    teste = ""
                    teste = v.varName
                    teste = teste.strip("]")
                    teste = teste.strip("x[")
                    teste = teste.split(",")
                    dic_alocacao[teste[2]] = FR[(teste[0],teste[1])]
                    d_LastAlocation[teste[2]] = FR[(teste[0],teste[1])]
            if "w[" in v.varName:
                if v.x > 1:
                    teste = ""
                    teste = v.varName
                    teste = teste.strip("w[")
                    teste = teste.strip("]")
                    teste = teste.split(",")
                    dic_check_massa[teste[0]] += TC[teste[3]] * v.x
            if "gd_n[" in v.varName:
                elemento = v.varName.split(",")
                elemento = elemento[1]
                elemento = elemento.strip("]")
                descarga = v.varName.split(",")
                descarga = descarga[0]
                descarga = descarga.strip("gd_n[")
                if v.x > 0 and (descarga,elemento) in GDW_n.keys():
                    if GDW_n[descarga,elemento] == 10:
                        otimizar_teor = 1
        dic_viagens = {}
        teste = 0
        dic_viagens_p_esc = {i:0 for i in E}
        for v in m.getVars():
            if "w[" in v.varName:
                if v.x > 1:
                    teste = ""
                    teste = v.varName
                    teste = teste.strip("]")
                    teste = teste.strip("w[")
                    teste = teste.split(",")
                    aux = [k for k in dic_alocacao.keys() if dic_alocacao[k] == teste[1]]
                    aux = [k for k in dic_alocacao.keys() if FR[(teste[1],teste[2])] in dic_alocacao[k]]
                    dic_viagens_p_esc[aux[0]]+= v.x
                    dic_viagens[(teste[0], teste[1], teste[2], teste[3],aux[0])] = v.x
        m.reset()

        return (dic_alocacao, dic_viagens, d_LastAlocation, status,dic_viagens_p_esc, otimizar_teor)
    else:
        status = 0
        m.reset()
        return ({}, {}, d_LastAlocation, status,{}, otimizar_teor)

