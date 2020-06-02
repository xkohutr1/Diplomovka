import numpy as np
import sympy as sp

#########################################Function for normal optimization ##############################################
class Derive:
    def __init__(self, Function, SepVariable, EqConstrains, InConstrains):

        try:
            from function import Separat_Varaible
            SepVariable = Separat_Varaible(SepVariable)
            SepVariable = SepVariable.SepVariables
        except:
            print('Nezadane optimalizacne premenne')

        try:
            Lagrangean = Lagrangean_EQ_constrains(SepVariable, EqConstrains, Function)
            Function = Lagrangean.Function
            SepVariable = Lagrangean.SepVariable
            var = Lagrangean.var
        except:
            var = [*SepVariable]
            print('Nezadane rovnostne ohranicenia')

        try:
            from function import Logarithmic_barrier
            InCon = Logarithmic_barrier(var, InConstrains)
            InConstrain = InCon.InConstrain_split
            CFunction = Function + InCon.InConstrain
            flag = 1
        except:
            CFunction = Function
            print('Zle zadane nerovnostne ohranicenia')

        D_function = {}
        SepFunction = {}
        for v in range(len(var)):
            derivation = sp.diff(CFunction, var[v])
            D_function[var[v]] = derivation
            derivation = sp.diff(Function, var[v])
            int_var = sp.Symbol(var[v])
            try:
                SepFunction[var[v]] = (str(sp.integrate(derivation, int_var)) + InConstrain[var[v]])   # trigintegrate nejdu trigonometricke funkcie
            except:
                SepFunction[var[v]] = (str(sp.integrate(derivation, int_var)))
        self.DFunctions = D_function
        self.Flag = flag
        self.SepFunction = SepFunction
        self.SepVariable = SepVariable
        self.Variable = var

class Logarithmic_barrier:
    def __init__(self, var, InConstrains):
        in_constrains = InConstrains.split(',')
        Constrain = []
        for i in range(len(in_constrains)):
            smaller = in_constrains[i].find("<=")
            bigger  = in_constrains[i].find(">=")
            if smaller != -1:
                constrain = in_constrains[i].split('<=')
                for ii in range(1,len(constrain),1):
                    Constrain.append('-tni*log(-1*((' + constrain[ii-1] + ')-(' + constrain[ii] + ')))')
            elif bigger != -1:
                constrain = in_constrains[i].split('>=')
                Constrain = []
                for ii in range(1, len(constrain), 1):
                    Constrain.append('-tni*log(-1*((' + constrain[ii] + ')-(' + constrain[ii-1] + ')))')
        Constrain_split = {}
        for i in range(len(var)):
            Constrain_split[var[i]] = ''
            for ii in range(len(Constrain)):
                if Constrain[ii].find(var[i]) != -1:
                    Constrain_split[var[i]] = Constrain_split[var[i]] + Constrain[ii]
        self.InConstrain = ''.join(Constrain)
        self.InConstrain_split = Constrain_split

class Separat_Varaible:
    def __init__(self, sep_var):
        sep_var = sep_var.split(';')
        sep_variables = {}
        for i in range(len(sep_var)):
            sep_var[i] = sep_var[i].replace('[','')
            sep_var[i] = sep_var[i].replace(']','')
            var = sep_var[i].split(',')
            if len(var) > 1:
                for ii in range(len(var)):
                    sep_variables[var[ii]] = ','.join(var)
            else:
                sep_variables[var[0]] = var[0]
        self.SepVariables = sep_variables

class Lagrangean_EQ_constrains:
    def __init__(self, SepVariable, EqConstrains, Function):
        EqConstrains = EqConstrains.split(',')
        constrain = []
        SepVariable_keys = [*SepVariable]
        for i in range(len(EqConstrains)):
            for ii in range(len(SepVariable_keys)):
                if (EqConstrains[i].find(SepVariable_keys[ii]) != -1):
                    ni = 'ni_' + str(i)
                    pom1 = SepVariable[SepVariable_keys[ii]] + ',' + ni
                    SepVariable[ni] = pom1
                    pom2 = SepVariable[SepVariable_keys[ii]].split(',')
                    for iii in range(len(pom2)):
                        SepVariable[pom2[iii]] = pom1
                    break
            pom_constrain = EqConstrains[i].split('=')
            constrain.append(ni + '*(' + pom_constrain[0] + '-1*(' + pom_constrain[1] + '))')
        constrain = ''.join(constrain)
        self.Function = Function + '+' + constrain
        self.SepVariable = SepVariable
        SepVariable_keys = [*SepVariable]
        self.var = SepVariable_keys

class Split_Data_Among_Workers:
    def __init__(self, SepVariable):
        SepVariable_keys = [*SepVariable]
        Split_data = []
        already_append = []
        for i in range(len(SepVariable_keys)):
            if (SepVariable_keys[i] in already_append) == False:
                var = SepVariable[SepVariable_keys[i]]
                var = var.split(',')
                already_append.extend(var)
                Split_data.append(var)
        self.Split_data = Split_data

class Worker_Funcion_data:
    def __init__(self, workers, workers_datas):
        data = {};
        for worker in workers:
            for opt_data in workers_datas:
                if (worker.c_id == opt_data.c_id) and (worker.ov == opt_data.var):
                    if worker.c_id in data:
                        data[worker.c_id].append([worker.df, worker.ov, opt_data.x_opt, worker.sf, worker.sv])
                    else:
                        data[worker.c_id] = []
                        data[worker.c_id].append([worker.df, worker.ov, opt_data.x_opt, worker.sf, worker.sv])
        self.Data = data


#############################################Functions for MPC##########################################################

class ss2de:
    def __init__(self, A,B,x,u):
        A = A.replace(' ', '')
        A = A.replace('[', '')
        A = A.replace(']', '')
        A = A.split(';')

        B = B.replace(' ', '')
        B = B.replace('[', '')
        B = B.replace(']', '')
        B = B.split(';')

        x = x.replace('[', '')
        x = x.replace(']', '')
        x = x.split(';')

        u = u.replace('[', '')
        u = u.replace(']', '')
        u = u.split(';')

        diff_equation = {}
        for i in range(len(x)):
            A_row = A[i].split(',')
            B_row = B[i].split(',')
            diff_row = []
            for ii in range(len(x)):
                diff_row.append('(' + A_row[ii] + '*' + x[ii] + ')')
            for ii in range(len(u)):
                diff_row.append('(' + B_row[ii] + '*' + u[ii]+')')
            diff_equation[x[i]] = '+'.join(diff_row)
        self.Model_Equation = diff_equation

class de2de:
    def __init__(self, Model_Equation):
        Model_Equation = Model_Equation.replace(' ','')
        Model_Equation = Model_Equation.split(';')
        diff_equation = {}
        for i in range(len(Model_Equation)):
            Model_Equation_row = Model_Equation[i].replace('\r\n','')
            Model_Equation_row = Model_Equation_row.split('=')
            dif_var = Model_Equation_row[0].replace('(k+1)','')
            dif_fun = Model_Equation_row[1]
            while(dif_fun.find('(k)')!= -1 ):
                dif_fun = dif_fun.replace('(k)', '')
            diff_equation[dif_var] = dif_fun
        self.Model_Equation = diff_equation

class norm2_power2:
    def __init__(self,matirx):
        matrix_row = matirx
        matrix_col = matirx
        norm_of_matrix = []
        for i in range(len(matrix_row)):
            norm_of_matrix.append('(' + matrix_row[i][0] + ')' + '*(' +matrix_col[i][0] + ')')
        self.sol = '+'.join(norm_of_matrix)

class matmul:
    def __init__(self,A,B):
        B_transpose = []
        pom = []
        if isinstance(B[0], list) == False:
            for j in range(len(B)):
                pom.append(B[j])
            B_transpose.append(pom)
        else:
            for j in range(len(B[0])):
                pom = []
                for i in range(len(B[0])):
                    pom.append(B[i][j])
            B_transpose.append(pom)

        C = []
        for i in range(len(A)):
            pom2= []
            for ii in range(len(B_transpose)):
                A_row = A[i]
                if isinstance(A_row,list) == False:
                    A_row = []
                    A_row.append(A[i])
                B_col = B_transpose[ii]
                pom = []
                for iii in range(len(A_row)):
                    if (A_row[iii] == '0'):
                        pom.append(str(A_row[iii]))
                    else:
                        pom.append(str(A_row[iii]) + '*(' + str(B_col[iii]) + ')')
                pom2.append('+'.join(pom))
            C.append(pom2)
        self.sol = C

class substitution:
    def __init__(self, sub_this_o,by_this_o,n,var):
        sub_var = sub_this_o.copy()
        sub_this = sub_this_o.copy()
        by_this = by_this_o.copy()
        for i in range(len(sub_var)):
            if isinstance(sub_var[i], list) == True:
                sub_variable = sub_var[i][0]
            else:
                sub_variable = sub_var[i]
            sub = by_this[sub_variable]
            for ii in range(len(var)):
                pom_variable = var[ii]
                if n != '':
                    sub = sub.replace(pom_variable,pom_variable + '_' + str(n))
                else:
                    sub = sub.replace(pom_variable, pom_variable)
            sub_this[i] = sub
        self.sol = sub_this

class Log_Barrier:
    def __init__(self, InConstrains,var,n):

        InConstrains = InConstrains.replace(' ','')
        in_constrains = InConstrains.split(',')
        Constrain = []
        if n != '':
            n = int(n) -1
            pom_str = '_'
        else:
            pom_str = ''
        for i in range(len(in_constrains)):
            smaller = in_constrains[i].find("<=")
            bigger  = in_constrains[i].find(">=")
            if smaller != -1:
                constrain = in_constrains[i].split('<=')
                for ii in range(1,len(constrain),1):
                    if ((constrain[ii] in var) == True):
                        cons1 = constrain[ii] + pom_str + str(n)
                    else:
                        cons1 = constrain[ii]
                    if ((constrain[ii-1] in var) == True):
                        cons2 = constrain[ii-1] + pom_str + str(n)
                    else:
                        cons2 = constrain[ii-1]

                    Constrain.append('-tni*log(-1*((' + cons2 + ')-(' + cons1 + ')))')
            elif bigger != -1:
                constrain = in_constrains[i].split('>=')
                Constrain = []
                for ii in range(1, len(constrain), 1):
                    if ((constrain[ii] in var)== True):
                        cons1 = constrain[ii] + pom_str + str(n)
                    else:
                        cons1 = constrain[ii]
                    if ((constrain[ii-1] in var)== True):
                        cons2 = constrain[ii] + pom_str + str(n)
                    else:
                        cons2 = constrain[ii-1]

                    Constrain.append('-tni*log(-1*((' + cons1 + ')-(' + cons2 + ')))')
        self.sol = ''.join(Constrain)

class web_data_processed:
    def __init__(self, data):
        data = data.replace(' ', '')
        data = data.replace('[','')
        data = data.replace(']', '')
        data = data.split(';')
        pom_data = []
        for i in range(len(data)):
            if data[i] != '':
                if len(data) == 1:
                    pom_data.append(data[i].split(','))
                    pom_data = pom_data[0]
                else:
                    pom_data.append(data[i].split(','))
        self.sol = pom_data

class Variables:
    def __init__(self, x,u):
        variable = []
        for i in range(len(x)):
            if isinstance(x[i], list) == True:
                for ii in range(len(x[i])):
                    variable.append(x[i][ii])
            else:
                variable.append(x[i])
        for i in range(len(u)):
            if isinstance(u[i], list) == True:
                for ii in range(len(u[i])):
                    variable.append(u[i][ii])
            else:
                variable.append(u[i])
        self.sol = variable

class substitute_numbers:
    def __init__(self, Funk,Constants):
        for i in range(len(Constants)):
            if isinstance(Constants[i], list) == True:
                const = Constants[i][0]
            else:
                const = Constants[i]
            const = const.split('=')
            Funk = Funk.replace(const[0],const[1])
        self.sol = Funk

class creat_functions:
    def __init__(self, Model_Equation,matrix_Q,matrix_R,InCons,Nmin,x_raw,u,x_ref,Constants):
        ############################################ Process data from the web #########################################
        Constants = web_data_processed(Constants)
        Constants = Constants.sol
        matrix_Q = web_data_processed(matrix_Q)
        matrix_Q = matrix_Q.sol
        matrix_R = web_data_processed(matrix_R)
        matrix_R = matrix_R.sol
        x_raw = web_data_processed(x_raw)
        x_raw = x_raw.sol
        x_ref = web_data_processed(x_ref)
        x_ref = x_ref.sol
        if (len(x_ref) != len(x_raw)):
            x_ref = [['0']*len(x_raw[0])]*len(x_raw)
        u = web_data_processed(u)
        u = u.sol

        variables = Variables(x_raw,u)
        variables = variables.sol

        model = substitution(x_raw, Model_Equation, '', variables)
        model = model.sol  # General Model
        for m in range(len(model)):
            pom_model = substitute_numbers(model[m], Constants)
            model[m] = pom_model.sol
        FUN = {}
        Nmin = int(Nmin) #Predikcny horizont
        for i in range(Nmin+1): #+1 pre vseobecnz model
            if i == Nmin:
                n = ''
                j = ''
            else:
                j = -1
                n = i+1
            ############################################################################################################
            x = []
            for ii in range(len(x_raw)):
                pom_str = '_' + str(n)
                if n == '':
                    pom_str = ''
                if isinstance(x_raw[ii], list) == True:
                    pom_x = x_raw[ii][0]
                else:
                    pom_x = x_raw[ii]
                #x.append('(' + x_raw[ii][0] + pom_str + '-(' + x_ref[ii][0] + ')' +')')  # Static reference tracking
                x.append('(' + pom_x + pom_str + '-(' + 'x_ref_' + str(ii) + ')' + ')')  # Dynamic reference tracking
            ########################################### (Q*x)'*(Q*x) ###################################################
            # Matrix multiplication [(N x N) x (N x 1)] --> (N x 1)
            Q_x = matmul(matrix_Q,x)
            Q_x = Q_x.sol

            # Norm of matrix (N x 1)'*(N x 1) --> (1 x 1)
            norm_Q_x = norm2_power2(Q_x)
            norm_Q_x = norm_Q_x.sol

            ########################################### (R*u)'*(R*u) ###################################################
            # Matrix multiplication [(N x N) x (N x 1)] --> (N x 1)
            var_u = u
            u_pom= ''
            if n != '':
                u_pom = '_' + str(n-1)
            if (isinstance(var_u[0], list) == True):
                var_u = [var[0] + u_pom for var in var_u]
            else:
                var_u = [var + u_pom for var in var_u]
            R_u = matmul(matrix_R, var_u)
            R_u = R_u.sol

            # Norm of matrix (N x 1)'*(N x 1) --> (1 x 1)
            norm_R_u = norm2_power2(R_u)
            norm_R_u = norm_R_u.sol

            ######################################### LOGARITHMIC BARRIER ##############################################
            log_fi = Log_Barrier(InCons,variables,n)
            log_fi = log_fi.sol

            ########################################## SEPARATE FUNCTION ###############################################
            name_of_function = 'FUN_' + str(n+j)
            pre_funk = '(' + norm_Q_x + '+' + norm_R_u + log_fi + ')'

            ####################################### CONSTANT SUBSTITUTION ##############################################
            pre_funk = substitute_numbers(pre_funk,Constants)
            FUN[name_of_function] = str(sp.simplify(pre_funk.sol))

        self.SepFunction = FUN
        self.Variables = variables
        self.GenModel = model

class distribute:
    def __init__(self, N_prediction,N_Clients):
        distribution = [0]*N_Clients
        n = 0
        for i in range(N_prediction):
            distribution[n] = distribution[n] + 1
            if n == N_Clients-1:
                n = 0
            else:
                n = n + 1
        self.sol = distribution

class substitut:
    def __init__(self, Funk, General_Model, Variables, k, status):
        GModel = General_Model.copy()
        if status == 'only sub':
            for i in range(len(Variables)):
                if i < len(GModel):  # kvoly vstupu ten je o jeden mensi
                    pom_k = k + 1
                else:
                    pom_k = k
                var_model = Variables[i] + '_' + str(pom_k)
                Funk = Funk.replace(Variables[i],var_model)
        else:
            for i in range(len(GModel)):
                for ii in range(len(Variables)):
                    var_model = Variables[ii] + '_' + str(k)
                    GModel[i] = GModel[i].replace(Variables[ii],var_model)
            if status == 'new':
                for ii in range(len(Variables)):
                    if ii == len(GModel):  # kvoly vstupu ten je o jeden mensi
                        k = k -1
                    Funk = Funk.replace(Variables[ii], Variables[ii] + '_' + str(k))
            for i in range(len(GModel)):
                var_model = Variables[i] + '_' + str(k+1)
                Funk = Funk.replace(var_model,'(' + GModel[i] + ')')
        self.sol = Funk

class decentralization:
    def __init__(self, Gmodel, vars, k, last_sequence):
        G_model = Gmodel.copy()
        vars = vars.copy()
        dec_funk = []
        eval_lambda_fun = []
        lambda_var = ['lambda'+str(i) + '_' + str(k) for i in range(len(G_model))]
        ro = '1'

        model = []
        for i in range(k,last_sequence,-1):
            G_model = Gmodel.copy()
            for ii in range(len(G_model)):
                for iii in range(len(vars)):
                    var_model = vars[iii] + '_' + str(i - 1)
                    G_model[ii] = G_model[ii].replace(vars[iii], var_model)
                if i == k:
                    model.append(G_model[ii])

            for ii in range(len(G_model)):
                for iii in range(len(G_model)):
                    model[ii] = model[ii].replace(vars[iii]+ '_' + str(i), '('+G_model[iii]+')')

        for i in range(len(model)):
            pre_var = vars[i] + '_' + str(k)
            pom_dec_funk = lambda_var[i] + '*' + '(' + model[i] + '-' + pre_var + ')' + '+(' + ro + '/2)' + '*' + '(' + model[i] + '-' + pre_var + ')^2'
            eval_lambda_fun.append('0' + '+' + ro + '*' + '(' + model[i] + '-' + pre_var + ')')
            dec_funk.append(pom_dec_funk)
        dec_funk = '+'.join(dec_funk)
        self.sol = str(sp.simplify(dec_funk))
        self.Lambda = lambda_var
        for iii in range(len(eval_lambda_fun)):
            for ii in range(len(vars)):
                for i in range(k,last_sequence-1,-1):
                    var_model = vars[ii] + '_' + str(i) + 's'
                    eval_lambda_fun[iii] = eval_lambda_fun[iii].replace(vars[ii] + '_' + str(i), var_model)
        self.Eval_lambda = eval_lambda_fun

class derive:
    def __init__(self, Funk, Variables, k, d, len_of_x):
        grad = []
        vars = []
        if d == 0:
            d = 1

        for i in range(k, k + d):
            for ii in range(len(Variables)):
                Funk = Funk.replace(Variables[ii] + '_' + str(i)+'s', Variables[ii] + '_' + str(i))

        for i in range(k,k+d):
            for ii in range(len(Variables)):
                if (ii > len_of_x-1):
                    vars.append(Variables[ii] + '_' + str(i))
                    der_var = sp.symbols(vars[-1])
                    grad.append(sp.diff(Funk, der_var))
                elif (k != 0) and (i == k):
                    vars.append(Variables[ii] + '_' + str(i))
                    der_var = sp.symbols(vars[-1])
                    grad.append(sp.diff(Funk, der_var))
                elif (k == 0)  and (i == k):
                    vars.append(Variables[ii] + '_' + str(i))
                    grad.append('0')
        self.sol = grad
        self.opt_vars = vars
        self.sep_fun = Funk
class inicial_conditions:
    def __init__(self, Variables, x_zero):
        x0 = []
        len_of_x = len(x_zero)
        for i in range(len(Variables)+len_of_x):
            if (i > len_of_x-1):
                x0.append('0')
            else:
                x0.append(x_zero[i][0])
        self.sol = x0

class MPC_Worker_Varialbe_value:
    def __init__(self, All_workers_data, MPC):
        All_variables = [worker.Variable for worker in All_workers_data]
        All_variables_values = [worker.Optimal_value for worker in All_workers_data]
        All_var_val = {};
        GModel = MPC.General_Model
        GModel = GModel.split(';')
        Variables = MPC.Variables
        Variables = Variables.split(';')
        x_referenc = MPC.x_referenc
        x_referenc = web_data_processed(x_referenc)
        x_referenc = x_referenc.sol

        New_variable = []
        for i in range(len(All_variables)):
            if All_variables[i].find('lambda') == -1:
                count_lambda = 0
                All_variables[i] = All_variables[i] + 's'
            else:
                for ii in range(i):
                    if (All_variables_values[i].find(All_variables[ii]) != -1):
                        All_variables_values[i] = All_variables_values[i].replace(All_variables[ii],str(All_variables_values[ii]))
                is_number = str(np.abs(sp.simplify(All_variables_values[i])))
                try:
                    is_number = float(is_number)
                    is_number = '5'
                except:
                    is_number = 'No number'
                if (is_number.isdigit() == False):
                    Lambda = All_variables[i].split('_')
                    k = int(Lambda[1])-1
                    check_variable = ''
                    New_variable.append(Variables[count_lambda] + '_' + str(k) + 's')
                    count_lambda = count_lambda + 1
            if All_variables[i].find('lambda') != -1:
                for ii in range(i):
                    if (All_variables_values[i].find(All_variables[ii]) != -1):
                        All_variables_values[i] = All_variables_values[i].replace(All_variables[ii],str(All_variables_values[ii]))
            All_var_val[All_variables[i]] = str(sp.simplify(All_variables_values[i]))

        New_variable_value = New_variable.copy()
        for i in range(len(New_variable)):
            k = New_variable[i].split('_')
            k = int(k[1].replace('s',''))
            check_variable = New_variable[i]

            while ((check_variable in All_variables) == False):
                Model = GModel.copy()
                for j in range(len(GModel)):
                    for jj in range(len(Variables)):
                        var_model = Variables[jj] + '_' + str(k - 1) + 's'
                        Model[j] = Model[j].replace(Variables[jj], var_model)
                    var = Variables[j] + '_' + str(k) + 's'
                    New_variable_value[i] = str(sp.simplify(New_variable_value[i].replace(var, Model[j])))
                check_variable = Variables[j] + '_' + str(k - 1) + 's'
                k = k - 1
            for ii in range(len(All_variables)):
                if (New_variable_value[i].find(All_variables[ii]) != -1):
                    New_variable_value[i] = New_variable_value[i].replace(All_variables[ii], str(All_variables_values[ii]))
            All_var_val[New_variable[i]] = str(sp.simplify(New_variable_value[i]))
        var_keys = [var for var in All_var_val.keys()]
        for i in range(len(var_keys)):
            if var_keys[i].find('lambda') != -1:
                for ii in range(len(var_keys)):
                    if (All_var_val[var_keys[i]].find(var_keys[ii]) != -1):
                        All_var_val[var_keys[i]] = All_var_val[var_keys[i]].replace(var_keys[ii],str(All_var_val[var_keys[ii]]))
                All_var_val[var_keys[i]] = str(sp.simplify(All_var_val[var_keys[i]]))

        for i in range(len(GModel)):
            variable = 'x_ref_' + str(i)
            All_var_val[variable] = str(x_referenc[i][0])
        self.sol = All_var_val
        self.reference = x_referenc

class MPC_Worker_Data_Grup:
    def __init__(self, Workers, Workers_data, All_workers_data):
        keys = [i for i in All_workers_data.keys()]
        data = []
        for worker in Workers:
            function = worker.Separate_Function
            gradient = worker.Gradient
            variable = worker.Optimization_Variables
            value = All_workers_data[variable + 's']
            for i in range(len(keys)):
                find_variable = keys[i]
                if (function.find(find_variable)) != -1 or (gradient.find(find_variable) != -1):
                    pom_value = All_workers_data[keys[i]]
                    function = function.replace(find_variable,'('+str(pom_value)+')')
                    gradient = gradient.replace(find_variable,'('+str(pom_value)+')')
            data.append([str(sp.simplify(gradient)), variable, str(sp.simplify(value)), str(sp.simplify(function))])
        self.sol = data

class Find_previous_input:
    def __init__(self, MPC):
        Variables = MPC.Variables
        Variables = Variables.split(';')
        GModel = MPC.General_Model
        GModel = GModel.split(';')
        var = [Variables[jj] + '_' + str(0) for jj in range(len(GModel),len(Variables),)]
        self.sol = var

class Calculate_criteria:
    def __init__(self, criteria, Workers_data_all):
        for var in Workers_data_all:
            if criteria.find(var):
                criteria = criteria.replace(var, Workers_data_all[var])
        criteria = np.abs(sp.simplify(criteria))
        self.sol = criteria

class Calculate_input_criteria:
    def __init__(self, old_data, Workers_data_all):
        keys = [i for i in old_data.keys()]
        criteria = 0
        for var in keys:
            new_value = float(Workers_data_all[var+'s'])
            old_value = float(old_data[var])
            criteria = criteria + np.power(new_value-old_value,2)
        criteria = np.sqrt(criteria)
        self.sol = criteria

class Simulation:
    def __init__(self, Workers_data_all,MPC):
        Variables = MPC.Variables
        Variables = Variables.split(';')
        GModel = MPC.General_Model
        GModel = GModel.split(';')
        x_referenc = MPC.x_referenc
        x_referenc = web_data_processed(x_referenc)
        x_referenc = x_referenc.sol

        var = [Variables[jj] + '_' + str(0) for jj in range(len(Variables))]
        norm = []
        for j in range(len(GModel)):
            for jj in range(len(Variables)):
                var_model = Variables[jj] + '_' + str(0) + 's'
                GModel[j] = GModel[j].replace(Variables[jj], '('+Workers_data_all[var_model]+')')
            GModel[j] = str(sp.simplify(GModel[j]))

            norm.append('(' + GModel[j] + '-' + x_referenc[j][0] + ')^2')
        norm = 'sqrt(' + '+'.join(norm) + ')'
        norm = sp.simplify(norm)

        input_val = []
        for i in range(len(x_referenc),len(Variables),1):
            var_model = Variables[i] + '_' + str(0) + 's'
            input_val.append(Workers_data_all[var_model])

        self.sol = GModel
        self.variable = var
        self.norm = norm
        self.input = input_val