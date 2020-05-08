function gdmethod(grad_data){
    /* Pomocne premenne */
    var epsilon = math.pow(1*10,-10);
    var td = 10;
    var kmax = 10000;
    //console.log(grad_data)
    /* Parameter for logarithmick barrier method */
    var ni = 0.7;
    var tni = 0.8;

    /* Back tracking */
    var alfa = 0.5;
    var beta = 0.7;

/*new Array(len).fill(1)*/
    var grad = [];
    var funk = [];
    var variable = [];
    var x0 = [];
    for (i = 0; i < grad_data.length; i++){

        var pom_g = grad_data[i][0];
        var pom_f = grad_data[i][3];

        while(String(pom_g).includes('**') == true){
            pom_g = pom_g.replace('**','^');
        }

        while(String(pom_f).includes('**') == true){
            pom_f = pom_f.replace('**','^');
        }

        grad.push(pom_g);
        funk.push(pom_f)

        variable.push(grad_data[i][1]);
        x0.push(parseFloat(grad_data[i][2]));
        if (String(grad_data[0][3]).includes('tni') == true){
            var pom_epsilon_ni = 1;
            var epsilon_ni = 0.00001
            var isset_tni = true
        }else{
            var pom_epsilon_ni = 0;
            var epsilon_ni = 0;
        }
    }

    if (isset_tni == true){
        variable.unshift('tni');
        x0.unshift(tni);
    }

    var x_v = x0;
    var eval_grad = [];
    var eval_funk = [];
    var item_grad = [];
    var item_funk = [];
    for (ii = 0; ii < grad.length; ii++){
        var pom_grad = String(grad[ii]);
        var pom_funk = String(funk[ii]);
        var item_g = {};
        var item_f = {};
        for (i = 0; i < variable.length; i++){
            var pom_var = String(variable[i]);
            if (String(pom_grad).includes(pom_var) == true){
                pom_x_v = parseFloat(x_v[i]);
                item_g[pom_var] = pom_x_v;
            }
            if (String(pom_funk).includes(pom_var) == true){
                pom_x_v = parseFloat(x_v[i]);
                item_f[pom_var] = pom_x_v;
            }
        }

        item_grad.push(item_g);
        pom_grad = math.evaluate(pom_grad,item_g);
        eval_grad.push(pom_grad);

        item_funk.push(item_f);
        pom_funk = math.evaluate(pom_funk,item_f);
        eval_funk.push(pom_funk);
    }
    ///////////// Pre Backtracking a Kriterium zastavenia ///////////////
    var ones = Array(eval_funk.length).fill(1);
    var FUNK = math.multiply(ones,eval_funk);
    var FUNK_stare = FUNK+100;
    var k = 0;

    while ((math.norm(FUNK_stare - FUNK,2) > epsilon) && (pom_epsilon_ni*x_v[0] >= epsilon_ni)){

        k++;
        ////////////////////// KROK O KTORY SA MAME POSUNUT ///////////////////
        da = math.dotMultiply(-1,eval_grad);

        //////////////////////// Backtracking /////////////////////
        var GRAD_DA = math.multiply(math.transpose(eval_grad),da);
        var t = td;
        x_v = x_v.flat();
        do{
            //////////EVALUACIA/////////
            t = beta*t;
            eval_funk_BT = [];
            for (ii = 0; ii < grad.length; ii++){
                pom_funk = String(funk[ii]);
                item_f = {};
                for (i = 0; i < variable.length; i++){
                    pom_var = String(variable[i]);
                    if (String(pom_funk).includes(pom_var) == true){
                        if (isset_tni == true){
                           if (i == 0){
                               item_f[pom_var] = x_v[i];
                           } else{
                               pom_x_v = parseFloat(x_v[i]);
                               pom_da = parseFloat(da[i-1]);
                               item_f[pom_var] = pom_x_v + t*pom_da;
                           }
                        }else {
                            pom_x_v = parseFloat(x_v[i]);
                            pom_da = parseFloat(da[i]);
                            item_f[pom_var] = pom_x_v + t*pom_da;
                        }
                    }
                }
                pom_funk = math.evaluate(pom_funk,item_f);
                eval_funk_BT.push(pom_funk);
            }

            var FUNK_B = math.multiply(ones,eval_funk_BT);
            if (typeof FUNK_B.im == 'undefined'){
                imag_FUNK_B = 0;
            }else {
                imag_FUNK_B = math.abs(FUNK_B.im);
                FUNK_B = FUNK_B.re;
            }

            ///////// Men kym nebude vyhovujuce /////////
        } while((FUNK_B > (FUNK + alfa*t*GRAD_DA)) || (imag_FUNK_B > 0));
        /*console.log('Backtracking')
        console.log(FUNK + alfa*t*GRAD_DA);
        console.log(FUNK_B);
        console.log(t);
        console.log('Backtracking')*/
        t_da = math.dotMultiply(t,da);  // Vypocet delta_x
        x_v = x_v.flat();
        if (isset_tni == true){
            x_v_tni = ni*x_v[0];
            x_v_x0 = math.evaluate(math.add(x_v.slice(1, x_v.length),t_da));

            x_v = []
            x_v.push(x_v_tni,x_v_x0)
        }else {
            x_v = math.evaluate(math.add(x_v,t_da));
        }
        x_v = x_v.flat();
        //////// Evalucaia //////////
        eval_grad = [];
        eval_funk = [];
        for (ii = 0; ii < grad.length; ii++){
            pom_grad = String(grad[ii]);
            pom_funk = String(funk[ii]);
            item_g = {};
            item_f = {};
            for (i = 0; i < variable.length; i++){
                pom_var = String(variable[i]);
                if (String(pom_grad).includes(pom_var) == true){
                    pom_x_v = parseFloat(x_v[i]);
                    item_g[pom_var] = pom_x_v;
                }
                if (String(pom_funk).includes(pom_var) == true){
                    pom_x_v = parseFloat(x_v[i]);
                    item_f[pom_var] = pom_x_v;
                }
            }
            pom_grad = math.evaluate(pom_grad,item_g);
            eval_grad.push(pom_grad);
            pom_funk = math.evaluate(pom_funk,item_f);
            eval_funk.push(pom_funk);
        }
        x_v = x_v.flat();
        var pom_funk = FUNK;
        FUNK = math.multiply(ones,eval_funk);
        FUNK_stare = pom_funk;
        /*console.log('--end--');
        console.log(t_da);
        console.log(x_v);
        console.log(math.norm(FUNK_stare - FUNK,2));
        console.log('--end--');*/
        if (k === kmax){
            break;
        }
    }

    if (isset_tni == true){
        solution = [x_v.slice(1, x_v.length),variable.slice(1, variable.length),k]
    }else {
        solution = [x_v,variable,k]
    }
    return solution
}