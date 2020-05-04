# Diplomovka
MPC-apk

treba vytvorit docker image cez build a cestu kde mame potrebne subory -> nazov romankohut/apk-for-decentralized-mpc
# docker build C:/Users/RomanK/Desktop/DIPLOMOVKA/Docker -t romankohut/apk-for-decentralized-mpc

push na docker hub ->
# docker push romankohut/apk-for-decentralized-mpc

Sever pojde na porte localhost:5000 ->
# docker run -it --rm -p 5000:5000 romankohut/apk-for-decentralized-mpc

Po pripojeni na localhost:5000 ->

1. Model predictiv control
2. Objavy sa moznost    a) vztvorit nove MPC 
			b) pripojit sa k existujucemu


a) Moznost vybrat si medzi Stavovim opisom alebo dif. rovnicami 
večšinou tesujem na systeme:

(* potrebne zadefinovat)

STATE SPACE
*A: [1,0;0,1]
*B: [1;1]

*x: [volitelne] --> [x1;x2]
*u: [volitelne] --> [u]
{"MUSIA SEDIET ROZMERI ZAPIS AKO V MATLABE ESTE SOM NEROBIL ALERTY"}
OPTIMIZATION set-up

*N: volitelne --> 5
*Q: [1,0;0,1]
*R: [1]
*x_0: [volitlene] --> [0;0]
*x_ref: [volitelne] ---> [5;5]

Ineqality C.: volitelne ale musia byt zo zadefinovanych premennych --> -3 <= u <= 3

NIEJE OSETRENE ZE JE CHYBA SERRVER NEBUDE VEDIET SPRACOVAT :( 

Po odoslani udajov (moze trva yaleyi na velkosti preikcneho horizontu)
sa otvoris tranka kde v tabulke su optimalizovane premenne.

STOP SIMULATION: zasatavy nadobro simulaciu
Hned vedla je okno pre zadefinovanie referencie (New Reference) treba opat vlozit
v spravnom tvare inak serrver zblbne --> [7;7] Potvrdzuje sa tlacidlom Send

                                 !!! AK CHCETE UKONCIT OPTIMALIYACIU TREBA POUZIT DISCONNECT !!!

"Dufam ze sa to nestane :( "
Ak serrver zblbne treba vymazat vsetky databazy:
"Len pocas vyvoja aplikacie potom to bude osetrene"
databazy ide opet vytvorit v paitone cez
from app import db
db.create_all()

			
