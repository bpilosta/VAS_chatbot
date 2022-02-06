from random import randint, random
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade import quit_spade
from argparse import ArgumentParser
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import time
import pandas as pd
from pyECLAT import ECLAT
import os
from csv import writer

#upravlja sustavom Chatbot
class AgentUpravitelj(Agent):
    class Upravljanje(CyclicBehaviour):
        async def on_start(self):
            print("Pokrenut Chatbot\n")
            self.ime = "Ja: "
            self.novac = randint(15000,30000)
        async def run(self):
                    upit = input(self.ime)
                    await self.pitajAgentaSugovornika(upit)
                    response = await self.cekajOdgovor()
                    #ovisno o odgovoru ili vraca odgovor direktno korisniku
                    #ili izvrsava neku od funkcionalnosti
                    if str(response) == 'Ja sam Chatbot, kako se ti zoves?':
                        if self.ime == "Ja: ": 
                            print("Chatbot:", response)
                            self.ime = input(self.ime)
                            print("Chatbot: Bok",self.ime)
                            self.ime = self.ime+": "
                        else:
                            print("Chatbot: Bok",self.ime[:-2],"ja sam Chatbot")
                            
                    elif str(response) == 'Ti se zoves':
                        if self.ime == "Ja: ":
                            print("Chatbot: Cekaj nisi mi jos rekao. Kako se zoves?")
                            self.ime = input(self.ime)
                            self.ime = self.ime+": "
                            print("Chatbot: U redu, od sad cu te zvati",self.ime[:-2])
                        else:
                            print("Chatbot:",response,self.ime[:-2])
                            
                    elif str(response) == "U redu, znaci...":
                        await self.pitajAgentaSkladiste("detalji")
                        odgovor = await self.cekajOdgovor()
                        print("Chatbot:",response)
                        print("Chatbot:",odgovor)
                        
                    elif str(response) == "Samo da pogledam koje procesore imamo":
                        await self.pitajAgentaSkladiste("komponente", 'procesori')
                        odgovor = await self.cekajOdgovorPolje()
                        print("Chatbot:", response)
                        print("Chatbot: Znaci imamo sljedece: ")
                        for item in odgovor:
                            print("\t",item)
                            
                    elif str(response) == "Samo da pogledam koje graficke imamo":
                        await self.pitajAgentaSkladiste("komponente", 'graficke kartice')
                        odgovor = await self.cekajOdgovorPolje()
                        print("Chatbot:", response)
                        print("Chatbot: Znaci imamo sljedece: ")
                        for item in odgovor:
                            print("\t",item)
                            
                    elif str(response) == "Samo da pogledam koje diskove imamo":
                        await self.pitajAgentaSkladiste("komponente", 'diskovi')
                        odgovor = await self.cekajOdgovorPolje()
                        print("Chatbot:", response)
                        print("Chatbot: Znaci imamo sljedece: ")
                        for item in odgovor:
                            print("\t",item)
                            
                    elif str(response) == "Samo da pogledam koja napajanja imamo":
                        await self.pitajAgentaSkladiste("komponente", 'napajanja')
                        odgovor = await self.cekajOdgovorPolje()
                        print("Chatbot:", response)
                        print("Chatbot: Znaci imamo sljedece: ")
                        for item in odgovor:
                            print("\t",item)
                            
                    elif str(response) == "Naravno, reci sto zelis.":
                        print("Chatbot:", response)
                        proizvod = input(self.ime)
                        await self.pitajAgentaProdavaca(proizvod.lower(), 'dodaj')
                        odgovor = await self.cekajOdgovorPolje()
                        if odgovor["message"] == "Nemam":
                            print("Chatbot: Nemamo tu komponentu!")
                        else:
                            print("Chatbot: U košaricu dodan proizvod ", proizvod)
                            print("Chatbot: U košarici imas: ")
                            for item in odgovor["kosarica"]["proizvodi"]:
                                print("\t",item)
                            print("Chatbot: Ukupna cijena košarice je: ",odgovor["kosarica"]["uk_cijena"])
                    
                    elif str(response) == "Samo da pitam prodavaca":
                        print("Chatbot:", response)
                        await self.pitajAgentaProdavaca('',"vrati")
                        odgovor = await self.cekajOdgovorPolje()
                        print("Chatbot: U košarici imas: ")
                        if len(odgovor["kosarica"]["proizvodi"]) == 0:
                            print("Chatbot: Nisi još ništa dodao u košaricu!!")
                        else:
                            for item in odgovor["kosarica"]["proizvodi"]:
                                print("\t",item)
                            print("Chatbot: Ukupna cijena košarice je: ",odgovor["kosarica"]["uk_cijena"])
                            
                    elif str(response) == "U redu, ispraznit cu kosaricu.":
                        print("Chatbot:", response)
                        await self.pitajAgentaProdavaca('',"isprazni")
                        odgovor = await self.cekajOdgovorPolje()
                        print("Chatbot: Tvoja kosarica za kupnju je prazna")     
                        print("Chatbot: Ukupna cijena košarice je: ",odgovor["kosarica"]["uk_cijena"])                      
                    
                    elif str(response) == "Na temelju onog što imaš u kosarici mogu ti preporuciti sljedece":
                        print("Chatbot:", response)
                        await self.pitajAgentaProdavaca('',"vrati")
                        odgovor = await self.cekajOdgovorPolje()
                        if len(odgovor["kosarica"]["proizvodi"]) == 0:
                            print("Chatbot: Nisi još ništa dodao u košaricu, dodaj nesto da vidim sto te zanima")
                        else:
                            await self.pitajAgentaPreporucitelja(odgovor["kosarica"]["proizvodi"],"preporuci")
                            odgovor2 = await self.cekajOdgovorPolje()
                            for i in odgovor2:
                                print("\t",i)
                                
                    elif str(response) == "Na racunu imas":
                        print("Chatbot:", response," ",self.novac," kuna")
                    
                    elif str(response) == "U redu, hvala na kupnji":
                        await self.pitajAgentaProdavaca('',"vrati")
                        odgovor = await self.cekajOdgovorPolje()
                        if len(odgovor["kosarica"]["proizvodi"]) == 0:
                            print("Chatbot: Nisi još ništa dodao u košaricu. Nemas sto kupiti!")
                        elif odgovor["kosarica"]["uk_cijena"] > self.novac:
                            print("Chatbot: Nazalost nemaš dovoljno novaca na računu da izvršiš kupnju")
                            print("Chatbot: Na racunu imas ",str(self.novac)," kuna")
                        else:
                            print("Chatbot:", response)
                            self.novac -= odgovor["kosarica"]["uk_cijena"]
                            await self.pitajAgentaProdavaca('',"isprazni")
                            odgovor2 = await self.cekajOdgovorPolje()
                            print("Chatbot: Tvoja kosarica za kupnju je prazna")
                            print("Chatbot: Na racunu imas jos ",str(self.novac)," kuna.")
                            await self.pitajAgentaPreporucitelja(odgovor["kosarica"]["proizvodi"],"zapamti")
                            odgovor3 = await self.cekajOdgovor()
                    else:
                        print("Chatbot:", response)
                        
        #funkcija za slanje upita agentu Skladiste
        async def pitajAgentaSkladiste(self, tema, tijelo=""):
            msg = spade.message.Message(
                to="agent@rec.foi.hr",
                body=tijelo,
                metadata={"ontology":tema})
            await self.send(msg)
        
        #funkcija za slanje upita agentu Sugovorniku
        async def pitajAgentaSugovornika(self, tijelo):
            msg = spade.message.Message(
                to="ime@rec.foi.hr",
                body=str(tijelo),
                metadata={"ontology":"upit"})
            await self.send(msg)
        
        #funkcija za slanje upita agentu Prodavacu
        async def pitajAgentaProdavaca(self, komponenta, tema):
            msg = spade.message.Message(
                to="posiljatelj@rec.foi.hr",
                body=komponenta,
                metadata={"ontology":tema})
            await self.send(msg)
        
        #funkcija za slanje upita agentu Preporucitelju
        async def pitajAgentaPreporucitelja(self, kosarica, tema):
            msg = spade.message.Message(
                to="primatelj@rec.foi.hr",
                body=str(kosarica),
                metadata={"ontology":tema})
            await self.send(msg)
        
        #cekanje na odgovor u stringu
        async def cekajOdgovor(self):
            odgovor = await self.receive(timeout=10)
            if odgovor:
                odgovor = odgovor.body
                return odgovor
        
        #cekanje na odgovor u nekoj strukturi
        async def cekajOdgovorPolje(self):
            odgovor = await self.receive(timeout=10)
            if odgovor:
                odgovor = eval(odgovor.body)
                return odgovor           
    
    #inicijalno postavljanje agenta Upravitelja
    async def setup(self):
        ponasanje = self.Upravljanje()

        self.add_behaviour(ponasanje)    

class AgentSugovornik(Agent):
    #ponasanje koje označava odgovar na korisnikov upit
    class Razgovor(CyclicBehaviour):    
        async def run(self):
            poruka = await self.receive()
            if poruka:
                upit = poruka.body
                vrati = self.agent.bot.get_response(upit)
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=str(vrati),
                )
                await self.send(msg)
   #inicijalno se trenira bot na temelju korpusa
    async def setup(self):
        ponasanje = self.Razgovor()
        self.bot = ChatBot("Bruno",
                storage_adapter='chatterbot.storage.SQLStorageAdapter',
                logic_adapters=[
                    {'import_path':'chatterbot.logic.BestMatch'},
                ],
            database_uri='sqlite:///sql_data/Chatbot.sqlite3')

        trainer = ChatterBotCorpusTrainer(self.bot)
        for i in range(5): 
            trainer.train(
                './chatbot_corpus.yml'
            )
        template = spade.template.Template(
            metadata={"ontology": "upit"}
        )
        self.add_behaviour(ponasanje, template)

class AgentProdavac(Agent):
    #ponasanje koje dodaje zeljene elemente u kosaricu
    class DodajUKosaricu(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                komponenta = poruka.body
                vrati = {'message':"", "kosarica":self.agent.kosarica}
                found_item = {}
                for vrsta in self.agent.komponente.keys():
                    for item in self.agent.komponente[vrsta]:
                        if komponenta == item["naziv"].lower():
                            found_item=item
                if len(found_item) == 0:
                    vrati["message"] = "Nemam"
                else:
                    self.agent.kosarica["proizvodi"].append(found_item["naziv"])
                    self.agent.kosarica["uk_cijena"]+=found_item["cijena"]
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=str(vrati),
                )
                await self.send(msg)
    #ponasanje koje vraca kosaricu i vrijednost kosarice
    class VratiKosaricu(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                vrati = {'message':"", "kosarica":self.agent.kosarica}
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=str(vrati),
                )
                await self.send(msg)
                
    class IsprazniKosaricu(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                self.agent.kosarica = {"proizvodi":[],"uk_cijena":0}
                vrati = {'message':"", "kosarica":self.agent.kosarica}
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=str(vrati),
                )
                await self.send(msg)
    
    #inicijalno postavljanje agenta Prodavaca
    async def setup(self):
        ponasanje = self.DodajUKosaricu()
        ponasanje2 = self.VratiKosaricu()
        ponasanje3 = self.IsprazniKosaricu()
        self.kosarica = {"proizvodi":[],"uk_cijena":0}
        
        self.komponente={'procesori':[
                {'naziv':'Ryzen73700X','cijena':2399},
                {'naziv':'Ryzen55600X','cijena':2599},
                {'naziv':'Ryzen95950X','cijena':6399},
                {'naziv':'i5-10400F','cijena':1199},
                {'naziv':'i5-12400F','cijena':1599},
                {'naziv':'i5-12600K','cijena':2599},
            ],
            "graficke kartice":[
                {'naziv':'RadeonRX6500XT','cijena':3299},
                {'naziv':'RadeonRX6600XT','cijena':5299},
                {'naziv':'RadeonRX6900XT','cijena':18999},
                {'naziv':'GTX1660Ti','cijena':4399},
                {'naziv':'RTX3060Ti','cijena':7999},
            ],
            "diskovi":[
                {'naziv':'Samsung980','kapacitet':250,'cijena':399},
                {'naziv':'Samsung870EVO','kapacitet':250,'cijena':528},
                {'naziv':'Samsung980PRO','kapacitet':250,'cijena':689},
                {'naziv':'Samsung870QVO','kapacitet':2048,'cijena':1514},
                {'naziv':'SamsungPM893','kapacitet':960,'cijena':1826},
            ],
            "napajanja":[
                {'naziv':'ThermaltakeSmart500', 'cijena':378},
                {'naziv':'CorsairCV650', 'cijena':519},
                {'naziv':'CorsairCX550M', 'cijena':608},
                {'naziv':'CorsairRM550x', 'cijena':919},
            ],
            }

        template = spade.template.Template(
            metadata={"ontology": "dodaj"}
        )
        template2 = spade.template.Template(
            metadata={"ontology": "vrati"}
        )
        template3 = spade.template.Template(
            metadata={"ontology": "isprazni"}
        )
        self.add_behaviour(ponasanje, template)
        self.add_behaviour(ponasanje2, template2)
        self.add_behaviour(ponasanje3, template3)         

class AgentSkladiste(Agent):
    #ponasanje koje vraca odgovor na komponente koje trgovina prodaje
    class PonasanjeVratiDetalje(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                vrati = "Mi ti od komponenti prodajemo procesore, grafičke karitce, diskove i napajanja. Što te tocno zanima?"
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=vrati,
                )
                await self.send(msg)
    
    #ponasanje koje vraca sve detalje zeljene komponente
    class PonasanjeVratiDetaljeKomponenti(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                tip = poruka.body
                vrati = []
                for komponenta in self.agent.komponente.keys():

                    if komponenta == tip:
                        for item in self.agent.komponente[komponenta]:
                            if komponenta == 'diskovi':
                                vrati.append(''.join([item['naziv']," ima cijenu ",str(item['cijena']), " i kapacitet ",str(item['kapacitet'])," GB"]))
                            else:
                                vrati.append(''.join([item['naziv']," ima cijenu ",str(item['cijena'])]))
                            
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=str(vrati),
                )
                await self.send(msg)
                    
    async def setup(self):
        ponasanje = self.PonasanjeVratiDetalje()
        ponasanje2 = self.PonasanjeVratiDetaljeKomponenti()
        self.komponente={'procesori':[
                {'naziv':'Ryzen73700X','cijena':2399},
                {'naziv':'Ryzen55600X','cijena':2599},
                {'naziv':'Ryzen95950X','cijena':6399},
                {'naziv':'i5-10400F','cijena':1199},
                {'naziv':'i5-12400F','cijena':1599},
                {'naziv':'i5-12600K','cijena':2599},
            ],
            "graficke kartice":[
                {'naziv':'RadeonRX6500XT','cijena':3299},
                {'naziv':'RadeonRX6600XT','cijena':5299},
                {'naziv':'RadeonRX6900XT','cijena':18999},
                {'naziv':'GTX1660Ti','cijena':4399},
                {'naziv':'RTX3060Ti','cijena':7999},
            ],
            "diskovi":[
                {'naziv':'Samsung980','kapacitet':250,'cijena':399},
                {'naziv':'Samsung870EVO','kapacitet':250,'cijena':528},
                {'naziv':'Samsung980PRO','kapacitet':250,'cijena':689},
                {'naziv':'Samsung870QVO','kapacitet':2048,'cijena':1514},
                {'naziv':'SamsungPM893','kapacitet':960,'cijena':1826},
            ],
            "napajanja":[
                {'naziv':'ThermaltakeSmart500', 'cijena':378},
                {'naziv':'CorsairCV650', 'cijena':519},
                {'naziv':'CorsairCX550M', 'cijena':608},
                {'naziv':'CorsairRM550x', 'cijena':919},
            ],
            }

        template = spade.template.Template(
            metadata={"ontology": "detalji"}
        )
        template2 = spade.template.Template(
            metadata={"ontology": "komponente"}
        )
        
        self.add_behaviour(ponasanje, template)    
        self.add_behaviour(ponasanje2, template2)

class AgentPreporucitelj(Agent):
    #ponasanje koje daje preporuku na temelju dane kosarice
    class Preporuci(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                recommend_from=eval(poruka.body)
                recommendations = []
                for el in recommend_from:
                    for item in self.agent.items_to_recommend:
                        if el in item:
                            item.remove(el)
                            if len(item) != 0 and item[0] not in recommendations and item[0] not in recommend_from:
                                recommendations.append(item[0])
                                break
                recommendations = list(dict.fromkeys(recommendations))
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body=str(recommendations),
                )
                await self.send(msg)
                
    #agent azurira svoju bazu za preporuke
    class AzurirajBazu(CyclicBehaviour):
        async def run(self):
            poruka = await self.receive()
            if poruka:
                za_dodati=eval(poruka.body)
                with open(os.path.join(os.path.dirname(__file__), "eclat/transakcije.csv"),'a', newline='') as f:
                    wr = writer(f)
                    wr.writerow(za_dodati)
                    f.close()
                #relearning
                training_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "eclat/transakcije.csv"),header=None)

                df = pd.DataFrame(training_data)
                eclat_instance = ECLAT(data=df,verbose=True)
                indexes, supports = eclat_instance.fit(min_support=0.02,
                                            min_combination=2,
                                            max_combination=2, separator=',')
                sorted_by_support = sorted(supports.items(), key=lambda item: item[1], reverse=True)
                self.agent.items_to_recommend = []
                        
                for item in sorted_by_support:
                    split_item = item[0].split(',')
                    self.agent.items_to_recommend.append([split_item[0],split_item[1]])    
                
                msg = spade.message.Message(
                    to="bruno_pilosta@rec.foi.hr",
                    body="vraceno",
                )
                await self.send(msg)
    
    #pokretanjem agenta izvodi se trening prema Eclat algoritmu
    async def setup(self):
        ponasanje = self.Preporuci()
        ponasanje2 = self.AzurirajBazu()
        training_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "eclat/transakcije.csv"),header=None)


        df = pd.DataFrame(training_data)
        eclat_instance = ECLAT(data=df,verbose=True)
        indexes, supports = eclat_instance.fit(min_support=0.02,
                                    min_combination=2,
                                    max_combination=2, separator=',')
        sorted_by_support = sorted(supports.items(), key=lambda item: item[1], reverse=True)
        self.items_to_recommend = []
                
        for item in sorted_by_support:
            split_item = item[0].split(',')
            self.items_to_recommend.append([split_item[0],split_item[1]])
        
        template = spade.template.Template(
            metadata={"ontology": "preporuci"}
        )
        template2 = spade.template.Template(
            metadata={"ontology": "zapamti"}
        )

        self.add_behaviour(ponasanje, template)
        self.add_behaviour(ponasanje2, template2)  

        
if __name__ == '__main__':
    k2 = AgentSkladiste("agent@rec.foi.hr", "tajna")
    pokretanje2 = k2.start()
    pokretanje2.result()
    
    k3 = AgentProdavac("posiljatelj@rec.foi.hr", "tajna")
    pokretanje3 = k3.start()
    pokretanje3.result()
    
    k4 = AgentPreporucitelj("primatelj@rec.foi.hr", "tajna")
    pokretanje4 = k4.start()
    pokretanje4.result()
    
    k5 = AgentSugovornik("ime@rec.foi.hr", "lozinka")
    pokretanje5 = k5.start()
    pokretanje5.result() 
    
    k1 = AgentUpravitelj("bruno_pilosta@rec.foi.hr", "bpilostaagent")
    pokretanje5 = k1.start()
    pokretanje5.result()
    

    while k2.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
        
    quit_spade()