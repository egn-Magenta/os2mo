---
title: MO manual
---

## Introduktion

OS2mo er bygget til at håndtere en eller flere organisationer (løn, administrativ, økonomi, MED/AMR mv.), dens medarbejdere og andre tilknyttede personer (eksterne konsulenter, praktikanter, mv.).

OS2mo implementerer den fællesoffentlige rammearkitektur og har to OIO-services implementeret (Organisation, Klassifikation).

Dette dokument beskriver en række grundbegreber og -logikker samt den funktionalitet, der er indlejret i brugergrænsefladen, jf. hhttps://morademo.magentahosted.dk/ bruce/bruce

Se [øvrig dokumentation](https://rammearkitektur.docs.magenta.dk/os2mo/index.html)

For at få et overblik over hvilke [integrationer](https://rammearkitektur.docs.magenta.dk/os2mo/arkitektur-design/overview.html) der er udviklet.

Der findes også en [implementeringshåndbog](https://rammearkitektur.docs.magenta.dk/os2mo/drift-support/cookbook.html)

## Overordnede begreber og fælles funktionalitet

### Organisation og Organisationsenhed

En organisation er en juridisk enhed med rettigheder og ansvar. Eksempler på organisationer er myndigheder (fx et ministerium, en styrelse, en kommune), NGO'er eller virksomheder.

En organisationsenhed er en del af en organisation og kan kun eksistere i forbindelse med denne. Eksempelvis kan et kontanthjælpskontor kun eksistere som en del af en kommune, og en it-afdeling eksisterer kun som en del af en virksomhed.

### Personer (medarbejder, praktikant, ekstern konsulent, etc.)

En person er en digital repræsentation af en fysisk person. Personer hentes typisk fra lønsystemet eller CPR-Registret og er altid indplaceret i organisationsenhed.

### Dobbelthistorik og Fortid, Nutid og Fremtid

[Dobbelthistorik](https://en.wikipedia.org/wiki/Bitemporal_Modeling), eller bitemporalitet, betyder, at både registreringstid og virkningstid håndteres:

**Registreringstid** er tidspunktet for selve registreringen, fx oprettelsen af en enhed eller en medarbejder. Denne ’tid’ optræder ikke i brugergrænsefladen, men vil altid kunne spores i databasen.

**Virkningstid** er den periode, inden for hvilken registreringen er gyldig, fx at en enhed skal eksistere fra 1. januar 2020 til 31. december 2024.

Det er altså i OS2mo muligt at have overblik over fortidige, nutidige og fremtidige registreringer vha. følgende tabs under hvert faneblad. Man kan altså se alle de ændringer der er foretaget over tid i brugergrænsefladen.

![image](../graphics/momanual/fortidnutidfremtid.png)

#### Afslut og Redigér ####

**Afslut**

![image](../graphics/momanual/Afslut.png)

Det er muligt at afslutte en registrering, sådan at fx en medarbejders engagement i organisationen bliver bragt til ophør på en specifik dato og vedkommendes konti i andre systemer (fx Active Directory) bliver nedlagt. Når datoen for afslutningen af ansættelsen oprinder, vil medarbejderens engagement flytte sig fra Nutid til Fortid.

**Redigér**

![image](../graphics/momanual/Rediger.png)

Det er muligt at redigere en registrering for at ændre en af registreringens oplysninger. Det kan fx være, at et telefonnummer skal redigeres, eller en tilknytningstype skal ændres. Hvis den nye tilknytningstype skal være gældende fra i dag, vil den gamle tilknytningstype rykke ned under Fortidstabben, og den ny tilknytningstype vil være gældende og at finde under Nutidstabben. På den måde er der synlig historik på alle de ændringer, man foretager.

I eksemplet nedenfor har Marie tilknytningen "Projektgruppemedlem", men det er planlagt, at hun skal være projektleder pr. en fremtidig dato, nemlig 01-02-2020, hvorfor ændringen nu kan ses under Fremtidstabben. Når datoen oprinder, vil hun ændringen bliver flyttet ned under Nutidstabben, mens den registrering, der findes under Nutidstabben, vil blive flyttet ned under Fortidstabben.

![image](../graphics/momanual/tilknytningstype.png)

Det skal bemærkes, at såfremt *startdatoen* ikke ændres, vil det resultere i en *overskrivning* af den eksisterende registrering, og der vil *ikke* blive oprettet historik på overskrivning, fordi det ikke bliver opfattet som en ændring, en en rettelse.

## OS2mo’s brugergrænseflade

OS2mo består af to moduler:
<ol>
  <li>Medarbejdermodulet, som håndterer tilknyttede personer og deres stamdata.</li>
  <li>Organisationsmodulet, som håndterer organisationsenheder og deres stamdata. Det er også muligt at skabe relationer mellem Organisationsenheder vha. modulet ’Organisationssammenkobling’.</li>
</ol>

De to moduler indeholder:

<ol>
<li>En Header – øverst.</li>
<li>Et Organisationshierarki – I venstre side (findes dog ikke i Medarbejder-delen).</li>
<li>En Detaljeside - I midten.</li>
<li>En række Hovedarbejdsgange – I højre side.</li>
</ol>

![image](../graphics/momanual/moduler.png)

### Header

OS2mo’s header ser således ud:

![image](../graphics/momanual/header.png)

Headeren består af følgende elementer:

<ol>
<li>OS2mo-ikon, der fører tilbage til startsiden.</li>
<li>Medarbejder- & Organisations-knapper, der leder til det ene og det andet modul.</li>
<li>Søgefunktion, som søger på medarbejdere, når man befinder sig i Medarbejdermodulet, og på enheder, når man er i Organisationsmodulet</li>
<li>Datovælger-knap, de kan spole i tid</li>
<li>Rapporter, hvor man kan tilgå rapporter</li>
<li>Indsigt</li>
<li>Sprog - dansk og engelsk</li>
<li>Log ind/ud-knap.</li>
</ol>

Yderligere forklaringer til **Søgefunktion**, **Rapporter** og **Indsigt**:

#### Søgefunktionen

![image](../graphics/momanual/Søg.png)

Søgefunktionen fungerer i kontekst med enten Medarbejderdelen eller Organisationsdelen:

Under Medarbejder-delen kan man søge på:

Brugernavn, dvs fornavn eller efternavn eller fuldt navn (ex Karen Hammer Nielsen)
BrugerVendt Nøgle (ex Bd5tr)
CPR-nummer uden bindestreg (ex 2908623439)

Under Organisationsdelen kan man søge på:

Administrativ- eller Løn-organisation (ex Svendborg Kommune)
Organisationsenhedsnavn (ex Egtved skole)
Enhedsnummer (BrugerVendt Nøgle, ex EgtSko)

#### Rapporter

![image](../graphics/momanual/Rapporter.png)

Rapporter er forskellige sammenstillinger af de data, der findes i OS2mo. Rapporterne bliver opdateret hver nat, så de altid indeholder de nyeste data. Rapporternes indhold afhænger af, hvad der er bestilt. En rapport kan fx være et link til en csv-fil, som angiver, hvem der er leder for hvem:

![image](../graphics/momanual/lederspænd.png)

#### Indsigt

KOMMER

![image](../graphics/momanual/fortidnutidfremtid.png)

### Organisationshierarki med mulighed for flere parallelle organisationer

I venstre side af skærmen findes et organisationshierarki, der giver overblik over organisationen og mulighed for navigation i den:

![image](../graphics/momanual/træ.png)

Bemærk, at det er muligt at have flere organisationer indlæst, fx den administrative organisation, lønorganisationen, MED/AMR-organisationen. I ovenstående eksempel er der tale om de to førstnævnte.

### Detaljeside

Når en organisationsenhed vælges, vil information om den være fordelt på en række faneblade:

![image](../graphics/momanual/fanebladeorganisation.png)

Det samme gør sig gældende, når en medarbejder vælges:

![image](../graphics/momanual/faneblademedarbejder.png)

#### Fanebladet Enhed

![image](../graphics/momanual/fanebladetenhed.png)

En organisationsenhed er en del af en organisation (fx Brønderslev Kommune) og kan kun eksistere i forbindelse med denne. Eksempelvis kan et kontanthjælpskontor kun eksistere som en del af en kommune.

Organisationsenheder kan spænde fra mindre enheder, som fx teams eller grupper, til store og komplekse enheder, som fx en forvaltning, der indeholder mange andre andre niveauer af underenheder.

Eksempler på organisationsenheder er teams, afdelinger, sektioner, kontorer, udvalg, projektgrupper, styregrupper, daginstitutioner, hold og lignende.

**Enhedstype** bruges til at skelne mellem de formål, enhederne har. Enhedstype skal bruges beskrivende og til at udsøge organisationsenheder af en bestemt enhedstype.
Eksempel: Afdeling, underafdeling, sektion, enhed, direktørområde, center.

**Enhedsniveau** udstilles fx i kommuner, der benytter lønsystemet SD-Løn, og angiver her, hvorvidt der er tale om en organisationsenhed, som tilhører den administrative organisation eller lønorganisationen. Enhedsniveau kan også blot benyttes til at angive et hierarki.

**Tidsregistrering** benyttes i nogle kommuner til at identificere, hvilken type tidsregistrering, enheden benytter sig af. Dette felt anvendes ikke i alle kommuner, og visning af det kan slås fra i MOs konfiguration.

**Overenhed** fortæller, hvilken enhed der ligger umiddelbart over de valgte enhed.

**Start- og slutdato** angiver hvornår sidste ændring på enheden er foretaget, og eventuelt hvornår den slutter.

#### Fanebladet Adresser

![image](../graphics/momanual/fanebladadresser.png)

Er beskrivelse af de forskellige kontaktformer, der er tilgængelige for organisationer, organisationsenheder og medarbejdere.

Eksempler på adressetyper er: Postadresse, email-adresse, EAN-nummer, P-nummer, Henvendelsessted, webadresse.

Det er muligt at behæfte en ‘Synlighed’ til alle Adressetyper. Synligheden ændrer ikke på, om adressen kan ses i MO, men indikerer overfor MOs brugere, om adressen må videregives, og anvendes i øvrigt af MOs integrationer til at afgøre, i hvilke sammenhænge en adresse må udstilles i (hjemmesider, rapporter, mv). Det kan typisk dreje sig om, at man ikke ønsker at udstille et telefonnummer på fx intranettet.

#### Fanebladet Engagementer

![image](../graphics/momanual/fanebladetengagementer.png)

Et engagement beskriver et forhold mellem en person og en organisationsenhed. Engagementet kan bruges til at beskrive den rolle, en person har i en organisation, fx at en person er "Projektansat" (**Engagementstype**) med **Stillingsbetegnelsen** ‘Jurist’.

**Primær** angiver hvorvidt der er tale om en primær ansættelse. Det har fx betydning for oprettelsen af Active Directory-kontoen.

#### Fanebladet Tilknytninger

![image](../graphics/momanual/fanebladettilknytninger.png)

En ‘Tilknytning’ definerer et forhold mellem en person og en organisationsenhed. Der er modsat engagementet ikke tale om en ansættelse, men om en funktion, en person udfylder i forbindelse med en anden organisationsenhed, end den vedkommende er ansat i.

Tilknytninger er typisk benyttet til at forbinde en medarbejder midlertidigt til en anden ehed ifm. et midlertidigt projekt. Det benyttes også hyppigt til at knytte medarbejdere til MED/AMR-organisationen. Det er også muligt at angive stefortrædere for fx tillidsrepræsentanter.

#### Fanebladet IT

![image](../graphics/momanual/fanebladetit.png)

Fanebladet ’IT’ giver et overblik over, hvilke it-systemer organisationsenheden benytter.

#### Fanebladet Roller

![image](../graphics/momanual/FanebladetRoller.png)

En Rolle definerer endnu et forhold mellem en person og en organisationsenhed. Der er typisk tale om en dagligdagsfunktion, som en afdeling har behov for. I eksemplet er der vist en asvarlig for organiseringen af sommerfesten.

Andre eksempler: Fraværsregistrant, DPO eller superbruger på en it-løsning.

#### Fanebladet Ledere

![image](../graphics/momanual/fanebladetledere.png)

En leder er en ansat, som har bestemmende indflydelse på organisationen ved hjælp af specifikke beføjelser og ansvarsområder.

Ledere kan beskrives vha:

- **Lederansvar** beskriver de ansvarstyper, en leder kan have. Eksempel: MUS-ansvarlig, Personaleansvarlig. En leder kan have flere ansvarsområder.
- **Ledertype** indikerer ofte lederens funktion og hierarkiske placering eller tilknytning til et specifikt organisatorisk niveau. Eksempel: Direktør, Beredskabschef, Centerchef, Institutionsleder.
- **Lederniveau** er en hierarkisk beskrivelse. Eksempel: Niveau 1, 2, 3.

For ledere gælder det (i Organisations-delen), at de er markeret med en stjerne (*), hvis de er nedarvede fra en overordnet organisationsenhed (se skærmbilledet ovenfor) som følge af at enheden ikke har en direkte leder. Nedarvede ledere kan ikke redigeres eller afsluttes fra andre steder end den organisationsenhed, de er direkte ledere for.
Det er desuden muligt at gøre en lederfunktion vakant, hvis den midlertidigt ikke er besat:

![image](../graphics/momanual/vakanteledere.png)

En lederfunktion gøres vakant ved at klikke på Redigeringsknappen og manuelt slette lederes navn:

![image](../graphics/momanual/sletleder.png)

#### Fanebladet KLE-opmærkninger

![image](../graphics/momanual/fanebladetkle.png)

Det er muligt at opmærke sine enheder med [KL's Emnesystematik (KLE)](http://www.kle-online.dk/soegning). Disse opmærkninger kan så sendes videre til andre systemer, der har behov for dem ifm. rettighedsstyring (fx FK ORG og OS2rollekatalog)

#### Fanebladet Relateret

Viser om en organisationsenhed har en relation til en anden:

![image](../graphics/momanual/fanebladetrelationer.png)

Relationer mellem enheder etableres og nedlægges i Organisationssammenkoblingsmodulet, som tilgås fra forsiden:

![image](../graphics/momanual/fanebladetrelationer.png)

#### Fanebladet Orlov

![image](../graphics/momanual/fanebladetorlov.png)

En ‘Orlov’ beskriver fritagelse for tjeneste eller arbejde i en periode. Man kan eventuelt bruge den til at suspendere en konto i Active Directory. Informationen sendes videre til andre systemer.

Eksempel: Uddannelsesorlov, Sygeorlov, Barselsorlov.

Fanebladet findes ikke i Organisations-delen.

#### Fanebladet Ejere

![image](../graphics/momanual/fanebladetejere.png)

Konceptet 'Ejer' benyttes til at foretage rollebaseret adgangsstyring. Det betyder at det er muligt at give visse personer rettigheder til at redigere i en specifik del af OS2mo, mens andre (adminsitratorer) har rettigheder til at redigere overalt i Os2mo. I eksemplet ovenfor har Alfa ret til at redigere i afdelingen "Teknik og Miljø", men hvis han prøver at at rette andre steder, vil han modtage denne besked.

Kræver at rettighedsstyring er sat op via [Keycloak](https://www.keycloak.org/)

![image](../graphics/momanual/ingenrettigheder.png)

## Hovedarbejdsgange

I Organisationsdelen findes fire arbejdsgange:

![image](../graphics/momanual/hovedarbejdsgangeorganisation.png)

1. Opret enhed
2. Omdøb enhed
3. Flyt enhed
4. Afslut enhed

I Medarbejder-delen er der fem:

![image](../graphics/momanual/hovedarbejdsgangemedarbejder.png)

1. Ny medarbejder
2. Orlov
3. Flyt engagement
4. Flyt mange engagementer
5. Opsig medarbejder

Som hovedregel gælder det, at arbejdsgange, der hidrører organisations-delen, udelukkende skal benyttes, hvis OS2mo er autoritativ for organisationen. Hvis organisationen hver nat hentes fra et andet system (fx KMD LOS), vil ændringer foretaget direkte i OS2mo blive overskrevet hver nat.

Såfremt lønsystemet er autoritativt for medarbejderne, gælder det ligeledes, at OS2mo’s medarbejder-arbejdsgange som hovedregel ikke bør benyttes, idet ændringer foretaget i OS2mo vil blive overskrevet af den næstkommende synkronisering fra lønsystemet.

*Det er altså kun, hvis OS2mo er autoritativ, at arbejdsgangene bør benyttes.*

Fælles for arbejdsgangene er, at en startdato skal angives (slutdatoen er optionel). Startdatoen kan være fortidig, nutidig eller fremtidig. Generelt er det sådan, at en organisationsenhed eller en medarbejder ikke må eksistere uden for hhv. den tilhørende overenhedens eller enheds gyldighedsperiode.

Oprettes en medarbejder med en fremtidig startdato, vil medarbejderen fremgå af ‘Fremtids’-tabben.

Oprettes en organisationsenhed med en fremtidig startdato, vil den kun fremgå af organisationstræet, hvis tidsmaskinen indstilles til den fremtidige dato. Ellers vil den først dukke op i organisationstræet på pågældende dato.

Når man opretter en organisationsenhed, kan man tilknytte en række informationer til den:

![image](../graphics/momanual/opretenhed.png)

Når man opretter en medarbejder, hentes vedkommende via indtastning af CPR-nummer fra CPR-registret (såfremt denne integration er tilvalgt). Man kan som med enheder tilknytte en række informationer til medarbejderen:

![image](../graphics/momanual/opretmedarbejder.png)

Når en enhed eller en medarbejder er oprettet, kan de fremsøges, og de informationer, der er tilknyttet til dem, vil fremgå af brugergrænsefladen.

Nogle steder vil det være muligt at redigere og afslutte enkelte registreringer. Hvor det ikke er muligt, er det pr. design. Fx er det ikke muligt at redigere eller afslutte en nedarvet leder.





