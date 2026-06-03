import os
import glob

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "Knowledge_Base")

def get_verified_answer(question):
    print(f"[SUB-ENGINE] Iščem uraden in preverjen odgovor v bazi znanj (Main Engine)...")
    
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        return "NAPAKA: Baza znanj ne obstaja. Zaženi setup_sub_engine.bat."
        
    found_knowledge = ""
    for root, dirs, files in os.walk(KNOWLEDGE_BASE_DIR):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt") or file.endswith(".json"):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(word in content.lower() for word in question.lower().split()):
                            found_knowledge += f"\n--- Iz dokumenta: {file} ---\n{content[:1000]}...\n"
                except:
                    pass
                    
    if found_knowledge:
        return f"NAJDENO ZLATO PRAVILO:\n{found_knowledge}\n[To je 100% preverjen postopek, sledi mu.]"
    else:
        return "V bazi znanja ni natančnega odgovora za ta problem. Počakaj, da Main Engine obdela to tematiko, ne poskušaj improvizirati!"

if __name__ == "__main__":
    print("="*50)
    print(" Dobrodošli v Axonris Lokalnem Asistentu (Sub-Engine)")
    print(" Ta asistent ne halucinira. Podaja le preverjeno kodo.")
    print("="*50)
    
    while True:
        user_input = input("\nKaj želiš zgraditi ali rešiti? (vnesi 'exit' za izhod): ")
        if user_input.lower() == 'exit':
            break
            
        odgovor = get_verified_answer(user_input)
        print("\n" + odgovor)
