# Diplomovka
MPC-apk

# Treba vytvorit docker image cez build a cestu kde mame potrebne subory -> npr. nazov romankohut/apk-for-decentralized-mpc
docker build C:/Users/RomanK/Desktop/DIPLOMOVKA/Docker -t romankohut/apk-for-decentralized-mpc

# Push na dockerhub ak by bolo potrebne
docker push romankohut/apk-for-decentralized-mpc

# Sever (Docker Image) sa dá spustiť pomocou nasledovného príkazu a pôjde na porte localhost:5000
docker run -it --rm -p 5000:5000 romankohut/apk-for-decentralized-mpc

# Po pripojeni na localhost:5000
Budeme mať na výber z dvoch možností -> Plne funkčné je zatial iba MPC

# Ako spustit MPC riadenie:

1. Model predictiv control
2. Objavý sa možnosť    a) vytvoriť nové MPC 
			b) pripojit sa k existujúcemu prediktívnemu riadeniu (Ak nejaké beží)

a) Moznost vybrat si medzi stavovím opisom alebo Dif. rovnicami
"Možné je zadefinovať iba stavové riadenie - čiže y,D,C Je nefunkčné"

Vo väčšine prípadoch sa do polí zapisujú matice, maticový zápis je rovnaký ako v MATLABE.

Príklad (State Space):
(* potrebne zadefinovat - Upozornia na to alerty)

STATE SPACE
*A: [1,0;0,1]
*B: [1;1]

*x: [volitelne] --> [x1;x2]
*u: [volitelne] --> [u]

*N: volitelné --> 5
*Q: [1,0;0,1]
*R: [1]
*x_0: [volitlene] --> [0;0]
*x_ref: [volitelne] ---> [5;5]

Ineqality C.: -3 <= u <= 3    "Použité premenné musia byť zadefinované v stavoch alebo vstupoch"

Po odoslaní udajov (može trva záleží na velkosti predikcneho horizontu)
sa otvorí stranka, kde v tabulke sú jednotlivé optimalizovane premenne, ktré optimalizujeme ako klient pomcou "JavaSript-Workera".

STOP SIMULATION: Zasatavý simuláciu
Hneď vedľa je okno pre zadefinovanie novej referencie (New Reference) treba opať vloziť
v spravnom tvare.

DISCONNECT: Slúži pre odhlásenie klienta z MPC ak nieje už dalši klient, ktorý by riešil optimalizáciu tak bude ukončená a vymazaná.


			
