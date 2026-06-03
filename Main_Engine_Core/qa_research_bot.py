import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI
import re

DASHBOARD_API = "http://127.0.0.1:8081/api"

def send_log(bot_name, msg):
    try:
        requests.post(f"{DASHBOARD_API}/log", json={"bot_name": bot_name, "msg": msg}, timeout=1)
    except:
        pass

MODEL_NAME = "qwen3.6-35b-a3b"

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

# --- ORODJA (TOOLS) ---
def search_web(query: str) -> str:
    msg = f"[TOOL] Iščem na DuckDuckGo: '{query}'"
    print(msg)
    send_log("QA Researcher", msg)
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=3)
        formatted = ""
        for r in results:
            formatted += f"Naslov: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}\n---\n"
        return formatted if formatted else "Ni zadetkov."
    except Exception as e:
        return f"Napaka pri iskanju: {e}"

def read_library(topic: str) -> str:
    msg = f"[TOOL] Preverjam interno knjižnico za temo: '{topic}'"
    print(msg)
    send_log("QA Researcher", msg)
    
    library_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Axonris_Library_Main_test_engine")
    if not os.path.exists(library_dir):
        return "Knjižnica je prazna ali ne obstaja."
        
    found_info = ""
    for root, dirs, files in os.walk(library_dir):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        if topic.lower() in content.lower():
                            found_info += f"Najdeno v {file}:\n{content[:500]}...\n---\n"
                except:
                    pass
    return found_info if found_info else f"Ni podatkov o '{topic}' v lokalni knjižnici. Potrebna raziskava na spletu."

def scrape_page(url: str) -> str:
    msg = f"[TOOL] Berem spletno stran: {url}"
    print(msg)
    send_log("QA Researcher", msg)
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]
    except Exception as e:
        return f"Napaka pri branju strani: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Poišče informacije na spletu (DuckDuckGo). Vrne naslove, URL-je in kratke povzetke.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Iskalni niz"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_page",
            "description": "Prebere celotno besedilo s specifične spletne strani (URL). Uporabi po tem, ko s search_web najdeš ustrezen URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL spletne strani"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_library",
            "description": "PRED ISKANJEM PO SPLETU vedno uporabi to orodje! Preveri, če podatek že obstaja v tvoji interni Axonris knjižnici.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Ključna beseda ali tema"}
                },
                "required": ["topic"]
            }
        }
    }
]

# --- GLAVNA FUNKCIJA AGENTA ---

def run_specialized_agent(ticket_id):
    tickets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_tickets")
    ticket_path = os.path.join(tickets_dir, f"{ticket_id}.json")
    
    if not os.path.exists(ticket_path):
        print(f"[QA RESEARCHER] Napaka: Ticket {ticket_id} ne obstaja.")
        return
        
    with open(ticket_path, "r", encoding="utf-8") as f:
        ticket = json.load(f)
        
    instruction = ticket.get("instruction", "Ni navodil.")
    msg = f"Prevzemam ticket {ticket_id}: {instruction}"
    print(f"\n[QA RESEARCHER] {msg}")
    send_log("QA Researcher", msg)
    
    prompt = f"""
    Ti si QA Researcher bot v Multi-Agent sistemu. 
    Tvoja naloga: {instruction}
    
    KRITIČNO PRAVILO: PREDEN UPORABIŠ `search_web`, OBVEZNO UPORABI `read_library`. 
    Najprej preveri interno zbirko znanja. Če tam najdeš odgovor, uporabi tistega in ZAKLJUČI NALOGO (ne hodi na splet). 
    Splet uporabi zgolj, če v knjižnici ni podatkov. Bodi strokoven in jedrnat.
    """
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Začni z raziskavo zdaj."}
    ]
    
    try:
        while True:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.3
            )
            
            response_message = response.choices[0].message
            
            if response_message.tool_calls:
                messages.append(response_message)
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search_web":
                        tool_response = search_web(arguments.get("query"))
                    elif function_name == "scrape_page":
                        tool_response = scrape_page(arguments.get("url"))
                    elif function_name == "read_library":
                        tool_response = read_library(arguments.get("topic"))
                    else:
                        tool_response = "Neznano orodje."
                        
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_response
                    })
            else:
                # Konec raziskave
                ans = response_message.content
                msg = f"Raziskava zaključena za ticket {ticket_id}."
                print(f"[QA RESEARCHER] {msg}")
                send_log("QA Researcher", msg)
                
                # Posodobi ticket
                ticket["status"] = "COMPLETED"
                ticket["result"] = ans
                ticket["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                with open(ticket_path, "w", encoding="utf-8") as f:
                    json.dump(ticket, f, indent=4)
                    
                break
                
    except Exception as e:
        msg_err = f"Napaka pri raziskovanju: {e}"
        print(f"[QA RESEARCHER] {msg_err}")
        send_log("QA Researcher ERROR", msg_err)
        ticket["status"] = "FAILED"
        ticket["result"] = str(e)
        with open(ticket_path, "w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_specialized_agent(sys.argv[1])
    else:
        print("[QA RESEARCHER] Napaka: Manjka Ticket ID. Uporaba: python qa_research_bot.py <ticket_id>")
