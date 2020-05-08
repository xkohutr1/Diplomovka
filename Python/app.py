############################################## OPTIMIZATION APK. #######################################################

################################################ REQUIRED LIBRARIES ####################################################
from flask import Flask, render_template, make_response
from flask import redirect, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import datetime
from flask_socketio import SocketIO, emit

# GLOBAL VARIABLE -> need to be replaced by something more effective
global g_status

####################################### DATABASE AND SERVER CONFIGURATION ##############################################
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY_BINDS = {'Clients': 'sqlite:///Clients.db',
                    'Worker': 'sqlite:///Worker.db',
                    'Worker_data': 'sqlite:///Worker_data.db',
                    'MPC_Worker': 'sqlite:///MPC_Worker.db',
                    'MPC_optimization': 'sqlite:///MPC_optimization.db',
                    'MPC_Worker_data': 'sqlite:///MPC_Worker_data.db'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '2020'
socketio = SocketIO(app)

# from app import db
# db.create_all()

############################################# STRUCTURES OF ALL DATABASE  ##############################################

################# DATBASE OF CLIENTS #######################
class Clients(db.Model):
    __bind_key__ = 'Clients'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, index=True)  # 1- Pripojený (Connected), 2- Priparvený na opt. (ready for optimization), 3- Odpojený (Disconnected) // MPC 1 -||-, 4- Pripraveny na OPT 5- Disconnect, 3 -||-
    MPC_optimization = db.Column(db.Integer, index=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

################# OPTIMIZATION DATABASES ###################
class Worker(db.Model):
    __bind_key__= 'Worker'
    id = db.Column(db.Integer, primary_key=True)
    df = db.Column(db.String(64), index=True)
    sf = db.Column(db.String(64), index=True)
    ov = db.Column(db.String(64), index=True)
    sv = db.Column(db.String(64), index=True)
    cons = db.Column(db.String(64), index=True)
    c_id = db.Column(db.Integer, index=True)  # ID-ecko klienta (ID of client, from Clients.db)

class Worker_data(db.Model):
    __bind_key__= 'Worker_data'
    id = db.Column(db.Integer, primary_key=True)
    var = db.Column(db.String(64), index=True)
    x_opt = db.Column(db.Float, index=True)
    ite = db.Column(db.Float, index=True)
    c_id = db.Column(db.Integer, index=True)  # ID-ecko klienta (ID of client, from Clients.db)
    status = db.Column(db.Integer, index=True)  # 1- Nástrel, 2- Nový údaj (výsledok optimalizácie), 3- Použití údaj (nástrel použitý v optimalizácií)

################# MPC DATABASES ###################
class MPC_optimization(db.Model):
    __bind_key__ = 'MPC_optimization'
    id = db.Column(db.Integer, primary_key=True)
    General_Model = db.Column(db.String(5000), index=True)
    General_Function = db.Column(db.String(10000), index=True)
    Variables = db.Column(db.String(64), index=True)
    x_referenc = db.Column(db.String(64), index=True)
    Nmin = db.Column(db.String(64), index=True)
    Nmax = db.Column(db.String(64), index=True)
    Client_id = db.Column(db.Integer, index=True)
    Status = db.Column(db.Integer, index=True)  # 1 - Optimization in progres, 2 - Optimization is completed

class MPC_Worker(db.Model):
    __bind_key__= 'MPC_Worker'
    id = db.Column(db.Integer, primary_key=True)
    Gradient = db.Column(db.String(10000), index=True)
    Optimization_Variables = db.Column(db.String(64), index=True)
    MPC_optimization_id = db.Column(db.Integer, index=True)
    Status = db.Column(db.Integer, index=True)
    Separate_Function = db.Column(db.String(5000), index=True)
    Client_id = db.Column(db.Integer, index=True)


class MPC_Worker_data(db.Model):
    __bind_key__= 'MPC_Worker_data'
    id = db.Column(db.Integer, primary_key=True)
    Variable = db.Column(db.String(64), index=True)
    Optimal_value = db.Column(db.String, index=True)
    Iteration = db.Column(db.Integer, index=True)
    Client_id = db.Column(db.Integer, index=True)
    Status = db.Column(db.Integer, index=True)  # 1- Nástrel, 2- Nový údaj (výsledok optimalizácie), 3- Použití údaj (nástrel použitý v optimalizácií), 4 - prisel join a je to stary udaj
    MPC_optimization_id = db.Column(db.Integer, index=True)

##################################################### INDEX HTML #######################################################
@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        action = request.form['button']
        ########################################## CONNECT CLIENT TO OPT. WORKBENCH ####################################
        if action == "Decentralised Optimization":  # Klien sa pripojil na server priradim mu ID a potrebne veci ...
            new_client = Clients(status = '1')
            try:
                db.session.add(new_client)
                db.session.commit()
                return render_template('connected.html', client = new_client,  c_id = new_client.id, status = g_status)
            except:
                return 'There was an issue whit your connection.'
        ########################################## CONNECT CLIENT TO MPC WORKBENCH #####################################
        elif action == "Model Predictiv Control":
            new_client = Clients(status='1')
            try:
                db.session.add(new_client)
                db.session.commit()
                try:
                    MPC = db.session.query(MPC_optimization).filter(MPC_optimization.Status == 1).all()
                    ID_MPC = []
                    for mpc in MPC:
                        ID_MPC.append(mpc.id)
                except:
                    ID_MPC = []
                return render_template('MPC_base.html', c_id=new_client.id, MPC=ID_MPC)
            except:
                return 'There was an issue whit your connection.'
        ################################### DATABASE 'SHOW' ONLY FOR DEVELOPMENT #########################################
        elif action == "Show Database":  # Ukaze celu databazu klientov a ich funkcií
            database = Clients.query.order_by(Clients.date_created).all()
            return render_template('index.html', show_me = database, show = 'hide')
        elif action == "Hide Database":  # Skryje celu databazu klientov a ich funkcií
            return render_template('index.html', show = 'show')
    else:
        return render_template('index.html', show = 'show')


########### Vseobecne optimalizacia (nacitanie ucelovky, opt premennych, ohraniceny a ulozenie do databaz)##############
@app.route('/start/<int:id>', methods=['POST','GET'])
def start_o(id):
    if request.method == 'POST':
        try:
            action = request.form['button']
            CFunction = request.form['CFunction']
            EqConstrains = request.form['EqConstrains']
            InConstrains = request.form['InConstrains']
            SepVariable = request.form['SepVariable']

            User = Clients.query.get_or_404(id)
            User.status = 2
            db.session.commit()
            # Kolko klientov je aktivnych
            try:
                N_of_Clients = Clients.query.filter(Clients.status == 2).count()
            except:
                return 'ERROR 1.0'

            # Funkcia pre decentraliyaciu OPT-PROBEM
            from function import Derive
            DFunction = Derive(CFunction, SepVariable, EqConstrains, InConstrains)
            SepVariable = DFunction.SepVariable
            #Variable = [item for sublist in SepVariable for item in sublist]
            #Variable = DFunction.Variable

            # vymaz predosle udaje
            try:
                db.session.query(Worker).delete()
                db.session.commit()
                db.session.query(Worker_data).delete()
                db.session.commit()
            except:
                print('Delet of database faild')
            number = 0


            C_client = Clients.query.filter(Clients.status == 2).all()
            from function import Split_Data_Among_Workers
            Split_data = Split_Data_Among_Workers(SepVariable)
            Split_data = Split_data.Split_data

            for i in range(len(Split_data)):
                if (number < N_of_Clients - 1):
                    number = number + 1
                else:
                    number = 0
                Variable = Split_data[i]
                for ii in range(len(Variable)):
                    variable = Variable[ii]
                    svariable = DFunction.SepVariable[variable]

                    client_id = C_client[number].id
                    sfunction = str(DFunction.SepFunction[variable])
                    dfunction = str(DFunction.DFunctions[variable])

                    all_variables = [*SepVariable]
                    for iii in range(len(all_variables)):
                        if (all_variables[iii] in sfunction) and (all_variables[iii] != variable):
                            #ADMM_data = ADMM_data()
                             print(all_variables[iii])

                    new_worker = Worker(df = dfunction, sf = sfunction , ov = variable, sv = svariable, cons = 'None', c_id = client_id)
                    db.session.add(new_worker)
                    db.session.commit()

                    worker_dataset = Worker_data(var = variable, x_opt = 2, ite = 0, c_id = client_id, status = 1)  # x_opt je v tomto pripade pociatocny nastrel :)
                    db.session.add(worker_dataset)
                    db.session.commit()

            if action == "Start New Optimization" and N_of_Clients > len(DFunction.Variable):  # Pripojenie klienta k serveru
                client = {'id': id}
                g_status = 'full'
                return render_template('connected.html', client = client, status = g_status)
            elif action == "Start New Optimization":
                g_status = 'in_progres'
                return render_template('optimization.html', c_id = id, status = g_status)
        except:
            User = Clients.query.get_or_404(id)
            User.status = 3
            db.session.commit()
            return render_template('index.html',show = 'show')


@app.route('/join/<int:id>', methods=['POST','GET'])  # Pridanie sa k prebiehajucej optimaliyacii
def join_o(id):
    User = Clients.query.get_or_404(id)
    User.status = 2
    db.session.commit()

    workers = Worker.query.all()
    workers_datas = Worker_data.query.all()
    clients = Clients.query.filter(Clients.status == 2).all()

    number_of_clients = len(clients)
    number_of_workers_datas = len(workers_datas)
    if number_of_workers_datas >= number_of_clients:
        number = 0
        for i in range(number_of_workers_datas):
            svariable = workers[i].sv
            if (number < number_of_clients - 1) and ((len(svariable) <= 1) or (svariable.find(workers[i+1].ov) == -1) or (svariable.find(workers[i-1].ov)== -1)):
                number = number + 1
            elif (len(svariable) > 1) and ((svariable.find(workers[i+1].ov) != -1) or (svariable.find(workers[i-1].ov) != -1)):
                number = number
            else:
                number = 0

            workers[i].c_id = clients[number].id
            workers_datas[i].c_id = clients[number].id
            db.session.commit()

        return render_template('optimization.html', c_id = id)
    else:
        return 'No optimization for you'


@socketio.on('connect_websocetio')
def sand_functions(masseg,id):
    print(masseg)
    workers = Worker.query.all()
    workers_datas = Worker_data.query.all()
    from function import Worker_Funcion_data
    W_data = Worker_Funcion_data(workers, workers_datas)
    data = W_data.Data
    socketio.emit('js_worker', data = data, broadcast=True)
    Worker_data.query.update({Worker_data.status: 3})
    db.session.commit()



@socketio.on('opt_solution')
def sand_functions(solution, client_id):
    opt_sol = solution[0]
    variable = solution[1]
    iteration = solution[2]
    worker_datasets = Worker_data.query.filter(Worker_data.c_id == client_id).all()
    for i in range(len(worker_datasets)):
        pom_sum = -1
        for var in variable:
            pom_sum += 1
            if worker_datasets[i].var == var:
                worker_datasets[i].x_opt = opt_sol[pom_sum]
                worker_datasets[i].ite = iteration
                worker_datasets[i].status = 2
                db.session.commit()
                #variable.remove(var)
    wait_for_worker = Worker_data.query.filter(Worker_data.status == 3).count()
    if wait_for_worker == 0:
        print('All worker complet optimization')
        workers = Worker.query.all()
        workers_datas = Worker_data.query.all()
        from function import Worker_Funcion_data
        W_data = Worker_Funcion_data(workers,workers_datas)
        data = W_data.Data
        socketio.emit('js_worker', data = data, broadcast=True)
    else:
        wait_for_worker = Worker_data.query.filter(Worker_data.status == 2).count()
        print('Caka sa na %d workerov na dokoncenie' %(wait_for_worker))


############################################ MODEL PREDICTIV CONTROL ###################################################
@app.route('/pass_to_startMPC/<int:id>', methods=['POST','GET'])
def pass_to_startMPC(id):
    return render_template('MPC_connected.html', c_id=id)

@app.route('/startMPC/<int:id>', methods=['POST','GET'])
def startMPC(id):
    ############################################ Data load from web ####################################################
    Model = request.form['Model_Repre']
    x = request.form['matrix_x']
    u = request.form['matrix_u']
    y = request.form['matrix_y']
    if Model == "StateSpace":
        A = request.form['matrix_A']
        B = request.form['matrix_B']
        C = request.form['matrix_C']
        D = request.form['matrix_D']
        from function import ss2de
        Model_Equation = ss2de(A,B,x,u)
        Model_Equation = Model_Equation.Model_Equation
    else:
        Model_Equation = request.form['DF_equation']
        from function import de2de
        Model_Equation = de2de(Model_Equation)
        Model_Equation = Model_Equation.Model_Equation

    matrix_Q = request.form['matrix_Q']
    matrix_R = request.form['matrix_R']
    InCons = request.form['InCons']
    EqCons = request.form['EqCons']
    Nmin = request.form['Nmin']
    Nmax = request.form['Nmax']
    x_ref = request.form['x_ref']
    x_zero = request.form['x_zero']

    Constants = request.form['Constants']

    from function import creat_functions
    Functions = creat_functions(Model_Equation,matrix_Q,matrix_R,InCons,Nmin,x,u,x_ref,Constants)
    Sep_Function = Functions.SepFunction
    Variables = Functions.Variables
    General_Model = Functions.GenModel

    from function import distribute
    from function import substitut
    from function import derive
    from function import decentralization
    from function import inicial_conditions

    ################################################# Server work code #################################################
    '''    try:
            db.session.query(MPC_Worker).delete()
            db.session.commit()
            db.session.query(MPC_Worker_data).delete()
            db.session.commit()
        except:
            print('Delet of database faild')
    '''
    ####################################### Upload optimization data to database #######################################
    General_Function = Sep_Function['FUN_']
    new_optimization = MPC_optimization(General_Model=';'.join(General_Model), General_Function=General_Function,
                                        Variables=';'.join(Variables), x_referenc= x_ref, Nmin=Nmin, Nmax=Nmax,
                                        Client_id=id, Status=1)
    db.session.add(new_optimization)
    db.session.commit()

    db.session.refresh(new_optimization)
    Optimization_id = new_optimization.id

    ######################################### Connect client to active clients #########################################
    User = Clients.query.get_or_404(id)
    User.status = 4
    User.MPC_optimization = Optimization_id
    db.session.commit()

    ########################################### How many cliens are active #############################################
    N_of_MPC_Clients = Clients.query.filter(Clients.status == 4). \
                       filter(Clients.MPC_optimization == Optimization_id).count()
    MPC_Clients = Clients.query.filter(Clients.status == 4). \
                  filter(Clients.MPC_optimization == Optimization_id).all()

    ##################################### Distribute optimization among active clients##################################
    Distribut_N = distribute(int(Nmin),N_of_MPC_Clients)
    Distribut_N = Distribut_N.sol

    kk = 0
    Funkcion = []
    sequence = []
    Lambda_var = []
    Lambda_optimal_value = {}
    for i in range(len(Distribut_N)):
        fun_pom = []
        if Distribut_N[i] != 0:
            ########################## Distribute given prediction horizon betwen clients ##############################
            for ii in range(Distribut_N[i]-1,0-1,-1):
                k = kk + ii
                Fun_name = 'FUN_' + str(k)
                Funk = Sep_Function[Fun_name]
                ####################################### SUBSTITUTION OF MODEL ##########################################
                sub_fun = Funk
                for iii in range(ii+1):
                    sub_fun = substitut(sub_fun, General_Model, Variables, k-iii, '')
                    sub_fun = sub_fun.sol
                fun_pom.append('(' + sub_fun + ')')

            if (k != 0):
                ########################################## ADMM DECENTRALISATION #######################################
                fun_decent = decentralization(General_Model, Variables, k)
                ############################################### LAMBDA #################################################
                pom_lambda = fun_decent.Lambda
                Lambda_var.append(pom_lambda)
                pom_lambda_fun = fun_decent.Eval_lambda
                for Lambda_i in range(len(pom_lambda)):
                    Lambda_optimal_value[pom_lambda[Lambda_i]] = pom_lambda_fun[Lambda_i]
                ########################################################################################################
                fun_decent = fun_decent.sol
                fun_pom.append('(' + fun_decent + ')')
            else:
                Lambda_var.append([''])

            sequence.append(k)
            Funkcion.append('+'.join(fun_pom))
            kk = k + Distribut_N[i]
        else:
            ###################################### Make new prediction horizon #########################################
            kk = kk + 1
            Fun_name = 'FUN_'
            Funk = Sep_Function[Fun_name]

            sub_fun = Funk
            sub_fun = substitut(sub_fun, General_Model, Variables, kk, 'new')
            sub_fun = sub_fun.sol

            sub_fun = substitut(sub_fun, General_Model, Variables, kk, '')
            sub_fun = sub_fun.sol

            fun_pom.append('(' + sub_fun + ')')
            fun_decent = decentralization(General_Model, Variables, kk)
            pom_lambda = fun_decent.Lambda
            Lambda_var.append(pom_lambda)
            pom_lambda_fun = fun_decent.Eval_lambda
            for Lambda_i in range(len(pom_lambda)):
                Lambda_optimal_value[pom_lambda[Lambda_i]] = pom_lambda_fun[Lambda_i]
            fun_decent = fun_decent.sol
            fun_pom.append('(' + fun_decent + ')')

            sequence.append(kk)
            Funkcion.append('+'.join(fun_pom))
    from function import web_data_processed
    x_zero = web_data_processed(x_zero)
    x_zero = x_zero.sol
    len_of_x = len(x_zero)
    ######################################### Upload data to database of workers #######################################
    for i in range(len(sequence)):
        k = sequence[i]  # ktore ostalo ako posledne dosadene
        d = Distribut_N[i]  # toto je pocet pred. horizontov na funkciu

        if k != 0:
            x_zero = [] # mame nastrel len pre x0

        Whole_Funk = '+'.join(Funkcion)

        Derive_funk = derive(Whole_Funk, Variables, k, d, len_of_x)
        Grad = Derive_funk.sol
        Opti_variables = Derive_funk.opt_vars

        Sep_fun = Funkcion[i]

        Inc_conditions = inicial_conditions(Opti_variables,x_zero)
        Inc_conditions = Inc_conditions.sol


        Client_id = MPC_Clients[i].id
        for ii in range(len(Opti_variables)):
            if (ii > 0):
                Sep_fun = '0'

            Gradient = str(Grad[ii])
            Optimization_Variables = Opti_variables[ii]
            new_worker = MPC_Worker(Gradient=Gradient, Optimization_Variables=Optimization_Variables,
                                    MPC_optimization_id=Optimization_id, Status=1,
                                    Separate_Function=Sep_fun, Client_id=Client_id)
            db.session.add(new_worker)
            db.session.commit()

            new_worker_data = MPC_Worker_data(Variable=Optimization_Variables, Optimal_value=Inc_conditions[ii],
                                              Iteration=0, Client_id=Client_id, Status=1,
                                              MPC_optimization_id=Optimization_id)
            db.session.add(new_worker_data)
            db.session.commit()

        if (Lambda_var[i][0] != ''):
            for ii in range(len(Lambda_var[i])):
                new_worker_data = MPC_Worker_data(Variable=Lambda_var[i][ii],
                                                  Optimal_value=Lambda_optimal_value[Lambda_var[i][ii]], Iteration=0,
                                                  Client_id=Client_id, Status=1, MPC_optimization_id=Optimization_id)
                db.session.add(new_worker_data)
                db.session.commit()
    return render_template('MPC_optimization.html', c_id = id)

########################################################## JOIN MPC ####################################################
@app.route('/joinMPC/<int:id>/<int:Optimization_id>', methods=['POST','GET'])
def joinMPC(id, Optimization_id):
    print('Join function')
    ######################################### Connect client to active clients #########################################
    Is_in_clients = db.session.query(Clients).filter(Clients.id == id). \
        filter(Clients.status != 1).count()

    if Is_in_clients == 0:
        User = Clients.query.get_or_404(id)
        User.status = 4
        User.MPC_optimization = Optimization_id
        db.session.commit()
        Disconnect = False
    else:
        Disconnect = True

    #################################### CALLCULTION IN PROGES WIAT !!!!!!!!! ##########################################
    wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
        filter(MPC_Worker_data.MPC_optimization_id == Optimization_id).count()

    while wait_for_worker < 0:
        wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                          filter(MPC_Worker_data.MPC_optimization_id == Optimization_id).count()



    ######################################### FIND MPC WHICH WE WANT OPTIMIZE ##########################################
    MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == Optimization_id).first()

    Nmin = MPC.Nmin
    Nmax = MPC.Nmax
    General_Model = MPC.General_Model
    General_Model = General_Model.split(';')
    Sep_Function = MPC.General_Function
    Variables = MPC.Variables
    Variables = Variables.split(';')

    from function import distribute, substitut, derive, decentralization, inicial_conditions
    from function import web_data_processed

    x_referenc = web_data_processed(MPC.x_referenc)
    x_referenc = x_referenc.sol

    ########################################### How many cliens are active #############################################
    N_of_MPC_Clients = Clients.query.filter(Clients.status == 4). \
                       filter(Clients.MPC_optimization == Optimization_id).count()
    MPC_Clients = Clients.query.filter(Clients.status == 4). \
                  filter(Clients.MPC_optimization == Optimization_id).all()

    ############################################ CHANGE STATUS OF OLD DATA #############################################
    Old_workers_data = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == Optimization_id).all()
    for old in Old_workers_data:
        old.Status = 4
        db.session.commit()

    Old_workers = db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id == Optimization_id).all()
    for old in Old_workers:
        old.Status = 4
        db.session.commit()
    ##################################### Distribute optimization among active clients##################################
    Distribut_N = distribute(int(Nmin),N_of_MPC_Clients)
    Distribut_N = Distribut_N.sol
    kk = 0
    Funkcion = []
    sequence = []
    Lambda_var = []
    Lambda_optimal_value = {}
    for i in range(len(Distribut_N)):
        fun_pom = []
        if Distribut_N[i] != 0:
            ########################## Distribute given prediction horizon betwen clients ##############################
            for ii in range(Distribut_N[i] - 1, 0 - 1, -1):
                k = kk + ii
                sub_fun = Sep_Function
                ####################################### SUBSTITUTION OF MODEL ##########################################
                for iii in range(ii + 1):
                    if iii == 0:
                        pom = 'only sub'
                    else:
                        pom = ''
                    sub_fun = substitut(sub_fun, General_Model, Variables, k - iii, pom)
                    sub_fun = sub_fun.sol
                    if pom == 'only sub':
                        sub_fun = substitut(sub_fun, General_Model, Variables, k - iii, '')
                        sub_fun = sub_fun.sol
                fun_pom.append('(' + sub_fun + ')')

            if (k != 0):
                ########################################## ADMM DECENTRALISATION #######################################
                fun_decent = decentralization(General_Model, Variables, k)
                ############################################### LAMBDA #################################################
                pom_lambda = fun_decent.Lambda
                Lambda_var.append(pom_lambda)
                pom_lambda_fun = fun_decent.Eval_lambda
                for Lambda_i in range(len(pom_lambda)):
                    Lambda_optimal_value[pom_lambda[Lambda_i]] = pom_lambda_fun[Lambda_i]
                ########################################################################################################
                fun_decent = fun_decent.sol
                fun_pom.append('(' + fun_decent + ')')
            else:
                Lambda_var.append([''])

            sequence.append(k)
            Funkcion.append('+'.join(fun_pom))
            kk = k + Distribut_N[i]
        else:
            ###################################### Make new prediction horizon #########################################
            sub_fun = Sep_Function
            sub_fun = substitut(sub_fun, General_Model, Variables, kk, 'only sub')
            sub_fun = sub_fun.sol
            sub_fun = substitut(sub_fun, General_Model, Variables, kk, '')
            sub_fun = sub_fun.sol
            fun_pom.append('(' + sub_fun + ')')
            fun_decent = decentralization(General_Model, Variables, kk)
            pom_lambda = fun_decent.Lambda
            Lambda_var.append(pom_lambda)
            pom_lambda_fun = fun_decent.Eval_lambda
            for Lambda_i in range(len(pom_lambda)):
                Lambda_optimal_value[pom_lambda[Lambda_i]] = pom_lambda_fun[Lambda_i]
            fun_decent = fun_decent.sol
            fun_pom.append('(' + fun_decent + ')')

            sequence.append(kk)
            Funkcion.append('+'.join(fun_pom))
            kk = kk + 1

    len_of_x = len(x_referenc)
    ######################################### Upload data to database of workers #######################################
    for i in range(len(sequence)):
        k = sequence[i]  # ktore ostalo ako posledne dosadene
        d = Distribut_N[i]  # toto je pocet pred. horizontov na funkciu

        Whole_Funk = '+'.join(Funkcion)

        Derive_funk = derive(Whole_Funk, Variables, k, d, len_of_x)
        Grad = Derive_funk.sol
        Opti_variables = Derive_funk.opt_vars

        Sep_fun = Funkcion[i]
        Client_id = MPC_Clients[i].id
        for ii in range(len(Opti_variables)):
            if (ii > 0):
                Sep_fun = '0'

            Gradient = str(Grad[ii])
            Optimization_Variables = Opti_variables[ii]
            ####################################### Extract old vlaue and delet ########################################
            try:
                Old_workers_data = MPC_Worker_data.query.filter(MPC_Worker_data.Variable == Optimization_Variables). \
                                              filter(MPC_Worker_data.MPC_optimization_id == Optimization_id).first()
                previous_inicial_conditions = Old_workers_data.Optimal_value
            except:
                previous_inicial_conditions = '0'
            ############################################################################################################
            new_worker = MPC_Worker(Gradient=Gradient, Optimization_Variables=Optimization_Variables,
                                    MPC_optimization_id=Optimization_id, Status=1,
                                    Separate_Function=Sep_fun, Client_id=Client_id)
            db.session.add(new_worker)
            db.session.commit()

            new_worker_data = MPC_Worker_data(Variable=Optimization_Variables, Optimal_value=previous_inicial_conditions,
                                              Iteration=0, Client_id=Client_id, Status=1,
                                              MPC_optimization_id=Optimization_id)
            db.session.add(new_worker_data)
            db.session.commit()

        if (Lambda_var[i][0] != ''):
            for ii in range(len(Lambda_var[i])):
                new_worker_data = MPC_Worker_data(Variable=Lambda_var[i][ii],
                                                  Optimal_value=Lambda_optimal_value[Lambda_var[i][ii]], Iteration=0,
                                                  Client_id=Client_id, Status=1, MPC_optimization_id=Optimization_id)
                db.session.add(new_worker_data)
                db.session.commit()

    try:
        db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == Optimization_id). \
            filter(MPC_Worker_data.Status != 1).delete()
        db.session.commit()
        db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id == Optimization_id). \
            filter(MPC_Worker.Status != 1).delete()
        db.session.commit()
    except:
        print('Nepodarilo sa deletnut stare udaje')

    if Disconnect == True:
        socketio.emit('reconnect', id)
    else:
        return render_template('MPC_optimization.html', c_id=id)


################################################# REFERENCE CHANGE FUNCTION ############################################
@socketio.on('change_reference')
def change_reference(x_referenc, c_id, status):
    if x_referenc != '':
        MPC_ID = db.session.query(MPC_Worker).filter(MPC_Worker.Client_id == c_id).first()
        MPC_ID = MPC_ID.MPC_optimization_id
        MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == MPC_ID).first()
        MPC.x_referenc = x_referenc
        db.session.commit()
        msg = 'Reference changed!'
    else:
        MPC_ID = db.session.query(MPC_Worker).filter(MPC_Worker.Client_id == c_id).first()
        MPC_ID = MPC_ID.MPC_optimization_id
        MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == MPC_ID).first()
        MPC.Status = status
        db.session.commit()
        msg = 'The simulation has been stopped'
    socketio.emit('reference_changed',msg)

########################################### WEBSOCKET FOR MPC OPTIMIZATION #############################################
@socketio.on('mpc_connect_websocetio')
def mpc_connect_websocetio(masseg, id, opt_id):
    print(masseg + ' -> MPC')

    from function import MPC_Worker_Data_Grup, MPC_Worker_Varialbe_value
    if id != '':
        Optimizatio_ID = MPC_Worker_data.query.filter(MPC_Worker_data.Client_id == id).first()
        Optimizatio_ID = Optimizatio_ID.MPC_optimization_id
    else:
        Optimizatio_ID = opt_id
    MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == Optimizatio_ID).first()
    Number_of_MPC_Workers = db.session.query(MPC_Worker). \
        filter(MPC_Worker.MPC_optimization_id == Optimizatio_ID).all()

    Workers_data_all = MPC_Worker_data.query.filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).all()
    Workers_data_all = MPC_Worker_Varialbe_value(Workers_data_all, MPC)
    Workers_data_all = Workers_data_all.sol

    used_ID = []
    data = {}

    for i in range(len(Number_of_MPC_Workers)):
        Worker_id = Number_of_MPC_Workers[i].Client_id
        if ((Worker_id in used_ID) == False):
            used_ID.append(Worker_id)

            MPC_Workers = db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id.like(Optimizatio_ID)). \
            filter(MPC_Worker.Client_id.like(Worker_id)).all()

            MPC_Workers_data = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID). \
            filter(MPC_Worker_data.Client_id.like(Worker_id)).all()

            W_data = MPC_Worker_Data_Grup(MPC_Workers, MPC_Workers_data, Workers_data_all)
            data[Worker_id] = W_data.sol

            for row in MPC_Workers_data:
                row.Status = 3
            db.session.commit()
    keys = [i for i in Workers_data_all.keys()]
    data['x'] = Workers_data_all[keys[0]]
    socketio.emit('js_worker', data=data, broadcast=True)

@socketio.on('ADMN_calulate')
def ADMN_calulate(solution, client_id):
    ###################################################### ADMM ########################################################
    epsilon = 0.01  # Stop criteria for ADMM
    opt_sol = solution[0]
    variable = solution[1]
    iteration = solution[2]
    MPC_Workers_data = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Client_id.like(client_id)).all()

    Optimizatio_ID = MPC_Worker_data.query.filter(MPC_Worker_data.Client_id == client_id).first()
    Optimizatio_ID = Optimizatio_ID.MPC_optimization_id

    ################################## FIND IF SOMEONE JOIN TO OPTIMIZZATION ###########################################
    Clients_in_disconnect = db.session.query(Clients).filter(Clients.MPC_optimization == Optimizatio_ID). \
        filter(Clients.status == 5).count()
    Clients_in_optimization = db.session.query(Clients).filter(Clients.MPC_optimization == Optimizatio_ID). \
        filter(Clients.status == 4).all()
    stop_someone_is_in_join = False
    for client in Clients_in_optimization:
        client_in_workers = db.session.query(MPC_Worker).filter(MPC_Worker.Client_id.like(client.id)). \
            filter(MPC_Worker.MPC_optimization_id == Optimizatio_ID).count()
        if (client_in_workers == 0) or (Clients_in_disconnect > 0):
            stop_someone_is_in_join = True

    if stop_someone_is_in_join == True:
        print('Stop someone is waiting')
    elif stop_someone_is_in_join == False:
        ############################################# UPDATE DATABAS AFTER OPTIMIZATION ################################
        for i in range(len(MPC_Workers_data)):
            for ii in range(len(variable)):
                if MPC_Workers_data[i].Variable == variable[ii]:
                    try:
                        MPC_Workers_data[i].Optimal_value = opt_sol[ii]
                        MPC_Workers_data[i].Iteration = iteration
                        MPC_Workers_data[i].Status = 2
                        db.session.commit()
                    except:
                        print('Neulozili sa udaje po optimalizacií')

        #################################### FIND IF ALL WORKERS END OPTIMISATION ##########################################
        wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                          filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).count()
        Lambda_in_wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                                    filter(MPC_Worker_data.Variable.contains('lambda')). \
                                    filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).count()
        '''        ################################## PATCH FOR DABASE MAGICK :D ##################################################
        if wait_for_worker-Lambda_in_wait_for_worker < 0:
            try:
                Workers = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                    filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).all()
                Lambdas = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                    filter(MPC_Worker_data.Variable.contains('lambda')). \
                    filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).all()
                for worker in Workers:
                    find_and_delet = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                        filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID). \
                        filter(MPC_optimization.Variables == worker.Variables).all()
                    find_and_delet2 = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                        filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID). \
                        filter(MPC_optimization.Variables == worker.Variables).all()
                    if len(find_and_delet) > 1:
                        for i in range(1,len(find_and_delet),1):
                            Delete = find_and_delet[i]
                            Delete.delete()
                            db.session.commit()
                            Delete = find_and_delet2[i]
                            Delete.delete()
                            db.session.commit()

                for Lambda in Lambdas:
                    find_and_delet = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                        filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID). \
                        filter(MPC_optimization.Variables == Lambda.Variables).all()
                    if len(find_and_delet) > 1:
                        for i in range(1,len(find_and_delet),1):
                            Delete = find_and_delet[i]
                            Delete.delete()
                            db.session.commit()
            except:
                print('Patch for database magick faild')'''

        #################################### FIND IF ALL WORKERS END OPTIMISATION ######################################
        wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                          filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).count()
        Lambda_in_wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                                    filter(MPC_Worker_data.Variable.contains('lambda')). \
                                    filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).count()

        ############################################# AFTER ALL WORKERS ARE DONE #######################################
        if wait_for_worker-Lambda_in_wait_for_worker == 0:

            print('All worker complet optimization')
            ######################################## WORK WHIT NEW DATA SET ################################################
            from function import MPC_Worker_Data_Grup, MPC_Worker_Varialbe_value, Calculate_criteria, Simulation
            try:
                MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == Optimizatio_ID).first()

                Number_of_MPC_Workers = db.session.query(MPC_Worker). \
                    filter(MPC_Worker.MPC_optimization_id == Optimizatio_ID).all()

                Workers_data_all = MPC_Worker_data.query.filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).all()
                Workers_data_all = MPC_Worker_Varialbe_value(Workers_data_all, MPC)
                Workers_data_all = Workers_data_all.sol
            except:
                print('Error during MPCjoin')

            used_ID = []
            data = {}
            criteria = []
            for i in range(len(Number_of_MPC_Workers)):
                Worker_id = Number_of_MPC_Workers[i].Client_id
                if ((Worker_id in used_ID) == False):
                    used_ID.append(Worker_id)
                    try:
                        MPC_Workers = db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id.like(Optimizatio_ID)). \
                            filter(MPC_Worker.Client_id.like(Worker_id)).all()

                        MPC_Workers_data = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID). \
                            filter(MPC_Worker_data.Client_id.like(Worker_id)).all()
                    except:
                        print('Cant find Optimizatio_ID')
                    ################################# PREPARATION OF DATA FOR OPTIMIZATION #################################
                    W_data = MPC_Worker_Data_Grup(MPC_Workers, MPC_Workers_data, Workers_data_all)
                    data[Worker_id] = W_data.sol
                    for row in MPC_Workers_data:
                        row.Status = 3
                        if (row.Variable.find('lambda') != -1):
                            Lambda = row.Variable
                            Lambda_value = Workers_data_all[Lambda]
                            Sym_val_of_lambda = row.Optimal_value
                            Sym_val_of_lambda = Sym_val_of_lambda.split('+')
                            Sym_val_of_lambda[0] = Lambda_value
                            pom = Sym_val_of_lambda[1:len(Sym_val_of_lambda)]
                            criteria.append('+'.join(pom))
                            Sym_val_of_lambda = '+'.join(Sym_val_of_lambda)
                            row.Optimal_value = Sym_val_of_lambda
                    db.session.commit()
            if len(criteria) == 0:
                ################################# THER IS NO NEED TO USE ADMM  NORMAL MPC ##################################
                print('NORMAL MPC')
                ####################### IN THIS POINT WE CAN DO WHATEVER WE WANT WHIT FOUND SOLUTION #######################
                # Workers_data_all <---- 'we can find optimal solution in this dictionary'
                # keys = [i for i in All_workers_data.keys()] <---- optimize variables
                # Workers_data_all[keys] <---- optimal values
                ################################# USE OF MPC OUTPUT IN SIMULATION ##########################################
                new_x0 = Simulation(Workers_data_all,MPC)
                value_x0 = new_x0.sol
                variable_x0 = new_x0.variable
                norm_x0 = new_x0.norm
                if MPC.Status != 2:
                    for i in range(len(value_x0)):
                        MPC_Workers_data = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Variable == variable_x0[i]). \
                                           filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).first()
                        MPC_Workers_data.Optimal_value = value_x0[i]
                        x0_id = MPC_Workers_data.Client_id
                        change_data = data[x0_id].copy()
                        for ii in range(len(change_data)):
                            if change_data[ii][1] == variable_x0[i]:
                                change_data[ii][2] = value_x0[i]
                        data[x0_id] = change_data
                        db.session.commit()

                    keys = [i for i in Workers_data_all.keys()]
                    data['x'] = Workers_data_all[keys[0]]
                    socketio.emit('js_worker', data=data, broadcast=True)
                else:
                    MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == Optimizatio_ID).first()
                    MPC.Status = 2
                    db.session.commit()
                    print('MPC bring system to referenc')
                    try:
                        db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id == Optimizatio_ID).delete()
                        db.session.commit()
                        db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).delete()
                        db.session.commit()
                    except:
                        print('Delet of database faild')
            else:
                ########################################### ADMM CALCULATION ###############################################
                criteria = '+'.join(criteria)
                criteria = Calculate_criteria(criteria,Workers_data_all)
                criteria = criteria.sol
                if criteria > epsilon:
                    data['x'] = 'ADMM'
                    #################################### ADMM NEED MORE ITERATIONS #########################################
                    socketio.emit('js_worker', data=data, broadcast=True)
                else:
                    ############################################ ADMM IS DONE ##############################################
                    print('ADMM DONE')
                    ####################### IN THIS POINT WE CAN DO WHATEVER WE WANT WHIT FOUND SOLUTION #######################
                    # Workers_data_all <---- 'we can find optimal solution in this dictionary'
                    # keys = [i for i in All_workers_data.keys()] <---- optimize variables
                    # Workers_data_all[keys] <---- optimal values
                    ################################# USE OF MPC OUTPUT IN SIMULATION ##########################################
                    new_x0 = Simulation(Workers_data_all,MPC)
                    value_x0 = new_x0.sol
                    variable_x0 = new_x0.variable
                    norm_x0 = new_x0.norm
                    if MPC.Status != 2:
                        for i in range(len(value_x0)):
                            MPC_Workers_data = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Variable == variable_x0[i]). \
                                               filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).first()
                            MPC_Workers_data.Optimal_value = value_x0[i]
                            x0_id = MPC_Workers_data.Client_id
                            change_data = data[x0_id].copy()
                            for ii in range(len(change_data)):
                                if change_data[ii][1] == variable_x0[i]:
                                    change_data[ii][2] = value_x0[i]
                            data[x0_id] = change_data
                            db.session.commit()

                        data['x'] = value_x0[0]
                        socketio.emit('js_worker', data=data, broadcast=True)
                    else:
                        print('MPC bring system to referenc')
                        try:
                            db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id == Optimizatio_ID).delete()
                            db.session.commit()
                            db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == Optimizatio_ID).delete()
                            db.session.commit()
                        except:
                            print('Delet of database faild')
        else:
            #################################### WAIT FOR ALL WORKERS TO END OPTIMIZATION ##################################
            print('WAIT FOR - %d WORKERS TO END OPTIMIZATION' % (wait_for_worker - Lambda_in_wait_for_worker))


############################################ DATABASE OF CLIENT ########################################################
@app.route('/delete/<int:id>')
def delete(id):
    Information_to_delete = Clients.query.get_or_404(id)
    try:
        db.session.delete(Information_to_delete)
        #db.session.query(Clients).delete()
        db.session.commit()
        db.session.query(MPC_Worker).filter(MPC_Worker.Client_id == id).delete()
        db.session.commit()
        db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Client_id == id).delete()
        db.session.commit()

        show_me = Clients.query.order_by(Clients.date_created).all()
        return render_template('index.html', show_me = show_me)
    except:
        return 'There was a problem deleting that'

@app.route('/disconnect/<int:id>', methods=['POST','GET'])
def disconnect(id):
    try:
        Client_to_disconnect = Clients.query.get_or_404(id)
        Client_to_disconnect.status = 5
        db.session.commit()

        MPC_id = db.session.query(Clients).filter(Clients.id == id).first()
        MPC_id = MPC_id.MPC_optimization

        Clients_in_optimization = db.session.query(Clients).filter(Clients.id != id). \
                                filter(Clients.status == 4). \
                                filter(Clients.MPC_optimization == MPC_id).count()

        #################################### CALLCULTION IN PROGES WIAT !!!!!!!!! ######################################
        wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
            filter(MPC_Worker_data.MPC_optimization_id == MPC_id).count()

        while wait_for_worker < 0:
            wait_for_worker = db.session.query(MPC_Worker_data).filter(MPC_Worker_data.Status == 3). \
                filter(MPC_Worker_data.MPC_optimization_id == MPC_id).count()
        if Clients_in_optimization > 0:
            client = db.session.query(Clients).filter(Clients.id != id). \
                filter(Clients.MPC_optimization == MPC_id).\
                filter(Clients.status == 4).first()
            joinMPC(client.id,MPC_id)

        else:
            db.session.query(MPC_Worker).filter(MPC_Worker.MPC_optimization_id == MPC_id).delete()
            db.session.commit()
            db.session.query(MPC_Worker_data).filter(MPC_Worker_data.MPC_optimization_id == MPC_id).delete()
            db.session.commit()
            MPC = db.session.query(MPC_optimization).filter(MPC_optimization.id == MPC_id).first()
            MPC.Status = 2
            db.session.commit()
    except:
        print('Pokazilo sa prepojene disconnect a join')

    Client_to_disconnect = Clients.query.get_or_404(id)
    Client_to_disconnect.status = 3
    db.session.commit()
    return render_template('index.html', show = 'show')

######################################### FLASK INITIALIZATION AND PORT OF SERVER ######################################
if __name__ == '__main__':
    g_status = 'new'
    socketio.run(app, host='0.0.0.0')
