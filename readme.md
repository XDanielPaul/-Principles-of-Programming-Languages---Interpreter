## **Dokumentácia ku implementácií 2. úlohe IPP 2019/2020**
Implementačná dokumentácia k 2. úlohe do IPP 2019/2020 
Meno a priezvisko: Daniel Paul 
Login: xpauld00
 
## Interpret kódu IPPcode20  
Interpret IPPcode20 je implementovaný v súbore *interpret.py*
### Triedy
**Interpret** - Načíta argumenty zo vstupu, skontroluje syntax a sématiku XML súboru, obsahuje cyklus na spracovanie inštrukcií
**Instruction** - Interpretuje inštrukcie, kontroluje, načítava argumenty
**Frames** - Pracuje s rámcami, premennými
**Variable** - Abstrakcia, objekt pre premennú
**Label** - Abstrakcia, objekt pre náveštia, obsahuje aj slovník všetkých náveští
**Constant** - Abstrakcia konštanty

### Funkcionalita
Intepretácia sa začína vykonávať v triede **Interpret**.
V jej konštruktore skontrolujú sa argumenty vstupu, do premennej **root** nahrá zdroj interpretovaného XML súboru, skontroluje sa syntax hlavičky a pokračuje sa do funkcie **processInstructions**.
V tejto funkcií sa skontroluje celková syntax a sématika XML súboru pomocou funkcie **checkSyntax**, kde sa elementy porovnávajú s predpokladanou štruktúrou a táto funkcia taktiež vráti hodnoty order jednotlivých inštrukcií.
Následne sa prednačítajú všetky náveštia (Labels) do dictionary v triede **Labels**.
Program v cykle vytvára objekty **Instruction**, ktoré obsahujú operačný kód inštrukcie, objekt XML prvku inštrukcie a načítané argumenty pomocou funkcie **loadArgs** - uložia sa do slovníku **args** typu {arg1 : objekt} (objekt - Variable, Constant, Label).
Program vstupuje do triedy **Instruction**, kde vo funkcií **resolveInstruction** interpretuje dané inštrukcie.
Pri každej inštrukcií sa kontroluje správny počet argumentov a aj ich typ pomocou funkcie **checkArgs**, kde sa porovnáva očakávaný počet argumentov inštrukcie a očakávaný typ sa kontroluje na základe zadaných objektov ako parametre funkcie.
Následne sa inštrukcie interpretujú v príslušných funkciách.
Premenné sú spracované v triede **Frames**, kde sa ukladajú do rámcov, ktoré sú reprezentované slovníkmi.
Sú tu funkcie na deklaráciu, inicializáciu premennej; zistenie rámcu premennej, alebo či sa premenná v danom rámci nachádza; nastavenie, či získanie hodnoty premennej.
Náveštia sú spracované v triede **Label**, kde sa ukladajú do slovníku **labels**.
Konštanty sú spracované v triede **Constant**, kde sa hodnoty dynamicky pretypujú na základe ich typu v argumente XML súboru.

## Použitie
Interpret sa používa pomocou _python3.8 interpret.py_ , pričom treba uviesť jeden z argumentov --source=FILE, alebo --input=FILE, kde --source je interpretovaný XML súbor a --input je vstup interpretovaného programu.
Pomôcka pre prácu so skriptom je implementovaná pomocou kontrolovania argumentu ($argv[1])  a zobrazí sa pomocou argumentu -\-help, tj.
_python3.8 interpret.py -\-help_
Ak pomôcku použijete nesprávne, skript sa ukončí s chybou 10.

## Testovací skript analyzátoru kódu parse.php a interprétu kódu IPPcode20
Testovací skript je implementovaný v súbore test.php
### Funkcionalita
Testovanie sa vykonáva v triede **Testing**
V konštruktore skript načíta zadané vstupné parametre a skontroluje nevalídne kombinácie vo funkcií **processArgs** pomocou **getopt** a uloží ich do pola **$arguments**, vytvorí základ HTML výstupu, ukončenie HTML výstupu a začne skenovať zložky podla zadaného argumentu **--directory=** vo funkcii **scandirectory**.
Ak je zadaný argument **--recursive**, tak sa naskenujú rekurzívne všetky podzložky. V prípade, že sa v zložke nájde súbor so suffixom .src, je takáto zložka posunutá do funkcie **testing**, kde sa vytvoria chýbajúce .out, .in, .rc súbory, otestujú sa src súbory podla toho, či bol zadaný parameter **--int-only** (testuje sa iba interpret.py),
**--parse-only** (testuje sa iba parse.php) a ak nie je zadaný žiadny z týchto parametrov, testujú sa obidva súbory.
Výsledky testov sú následne posúvané ako parametre do funkcie **htmladdrow**, ktorá z nich vytvorí výstupný HTML formát, na ktorom sa výsledky testovania zobrazia.

## Použitie
Interpret sa používa pomocou _php7.4 test.php_ , pričom je možné uviesť parametre:
* **--recursive** - rekurzívne prehľadáva zložky 
* **--directory** - zložka s testami. Ak nie je zadaná je ako predvolená použitá koreňová zložka
*  **--parse-script** - cesta k parse.php
* **--int-script** - cesta k interpret.py
* **--parse-only** - testuje sa iba parse.php
* **--int-only** - testuje sa iba interpret.py
* **--jexamxml** - cesta k jexamxml súboru, ktorý testuje iba parse.php pri **--parse-only**. Ak argument nie je zadaný, predvolená cesta je **/pub/courses/ipp/jexamxml/jexamxml.jar**
* 
Pomôcka pre prácu so skriptom je implementovaná pomocou kontrolovania argumentu ($argv[1])  a zobrazí sa pomocou argumentu -\-help, tj.
_php7.4 test.php -\-help_
Ak pomôcku použijete nesprávne, skript sa ukončí s chybou 10.






