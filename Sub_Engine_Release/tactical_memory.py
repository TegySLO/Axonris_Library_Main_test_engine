import os
import hashlib
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class TacticalMemory:
    """
    Taktini Spomin (Tactical Memory) - Prepreuje dvojno branje (caching) in 
    omogoa parametrino ekstrakcijo besedila (varevanje s tokeni/RAM-om).
    """
    def __init__(self, base_dir):
        self.cache_dir = os.path.join(base_dir, "knowledge_base", ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._clean_old_cache(days=7) # Po 7 dneh pobriemo (Garbage Collection)

    def _get_hash(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def _clean_old_cache(self, days=7):
        try:
            now = datetime.now()
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if now - file_time > timedelta(days=days):
                        os.remove(filepath)
        except Exception:
            pass

    def _fetch_url_content(self, url: str) -> str:
        """Pobere celotno vsebino strani s spleta."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Odstranimo nepotrebne scripte
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator=' ', strip=True)

    def _extract_parameters(self, full_text: str, parameters: str) -> str:
        """
        Namesto da LLM-u vrne 10.000 besed (in ga zrui), ta funkcija lokalno poie 
        kljune besede iz `parameters` in izlui kontekst okoli njih.
        """
        if not parameters or parameters.lower() == "all":
            return full_text[:3000] # Omejitev na max dolino za varnost
            
        keywords = parameters.lower().split()
        text_lower = full_text.lower()
        
        extracted_chunks = []
        last_index = -1
        
        # Poiemo ujemanja in vzamemo 300 znakov okoli vsake kljune besede
        for kw in keywords:
            idx = text_lower.find(kw)
            if idx != -1 and abs(idx - last_index) > 300:
                start = max(0, idx - 200)
                end = min(len(full_text), idx + 800)
                extracted_chunks.append(full_text[start:end])
                last_index = idx
                
        if not extracted_chunks:
            # e ni specifinih kljunih besed, vrnemo zaetek
            return full_text[:2000]
            
        final_text = "\n[...]\n".join(extracted_chunks)
        return final_text[:3000] # Absolutni maksimum

    def analyze_content(self, source: str, parameters: str = "all") -> str:
        """
        Glavna vstopna toka. Prebere lokalno datoteko ali URL in izlui 
        samo podatke, pomembne za `parameters`.
        """
        cache_key = self._get_hash(source) + ".json"
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        full_text = ""
        is_cached = False
        
        # 1. Preverimo Cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    full_text = data.get("content", "")
                    is_cached = True
            except:
                pass
                
        # 2. Pridobimo vsebino (e ni v cache)
        if not full_text:
            try:
                if source.startswith("http://") or source.startswith("https://"):
                    full_text = self._fetch_url_content(source)
                elif os.path.exists(source):
                    with open(source, "r", encoding="utf-8") as f:
                        full_text = f.read()
                else:
                    return f"Napaka: Vir {source} ne obstaja."
                    
                # Shranimo v cache za naslednji
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump({"source": source, "content": full_text, "cached_at": datetime.now().isoformat()}, f)
            except Exception as e:
                return f"Napaka pri branju vira: {e}"
                
        # 3. Parametrina Ekstrakcija (Zaita LLM Contexta)
        result = self._extract_parameters(full_text, parameters)
        
        prefix = f"[V ROBU] (Vir {'iz CACHE-a' if is_cached else 'SVEE PREBRANO'}): "
        return prefix + "\n" + result

if __name__ == "__main__":
    # Testiranje modula
    tm = TacticalMemory(os.path.dirname(os.path.dirname(__file__)))
    print("Preverjam Tactical Memory...")
