import os
import json
import time
import hashlib
import requests
import networkx as nx
from filelock import FileLock
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel  # ✅ updated import
import torch  # ✅ added for embedding
import faiss
import numpy as np
from openai import OpenAI
import re
load_dotenv()

class AutoLinker:
    def __init__(self, graph_path: str,
                 llm_api_key: Optional[str] = None,
                 llm_endpoint: Optional[str] = None,
                 faiss_index_path: str = "faiss_index.index"):
        self.graph_path = "law_graphTest.gpickle"
        self.graph_lock_path = f"{graph_path}.lock"
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY")
        self.llm_endpoint = llm_endpoint or os.getenv("LLM_ENDPOINT", "http://localhost:8000/generate")
        self.faiss_index_path = faiss_index_path

        #  Replace SentenceTransformer with inLegalBERT
        self.tokenizer = AutoTokenizer.from_pretrained("law-ai/InLegalBERT")
        self.model = AutoModel.from_pretrained("law-ai/InLegalBERT")
        self.model.eval()

        self.graph = None
        self.node_ids = []
        self.embeddings = []
        self.texts = []

        #UPDATE TO SEPERATE ARTICLES AND PRINCIPLES
        self.article_index = None
        self.article_ids = []
        self.article_texts = []
        self.principle_index = None
        self.principle_ids = []
        self.principle_texts = []

        self.index = None
        self._load_graph()
        print("building or loading FAISS index...")
        self._build_or_load_faiss()
        print("FAISS index ready.")

    def _normalize_text(self, item: Any) -> str:
        """
        Ensures that the input is always a string.
        If it's a dict, tries 'description', then 'title', then stringifies.
        If it's a list, joins all items as strings.
        """
        if isinstance(item, dict):
            return item.get("description") or item.get("title") or str(item)
        elif isinstance(item, list):
            return " ".join([self._normalize_text(x) for x in item])
        return str(item)

        


    def _find_article_by_number_or_title(self, article_str: str) -> Optional[str]:
        """
        Try to extract article number (e.g., '19', '22', '31A') or normalized title from the LLM string and match directly.
        Returns node_id if found, else None.
        """
        # Try to extract article number (e.g., Article 19, Article 19(1)(a), Article 31A)
        m = re.search(r"Article\s*(\d+[A-Z]?)(?:\([^)]+\))*", article_str, re.IGNORECASE)
        if m:
            art_num = m.group(1)
            for nid, data in self.graph.nodes(data=True):
                if data.get("type") == "article" and str(data.get("number", "")).upper() == art_num.upper():
                    return nid
        # Try to match by normalized title
        norm_title = article_str.lower().strip()
        for nid, data in self.graph.nodes(data=True):
            if data.get("type") == "article":
                title = str(data.get("title", "")).lower().strip()
                if title and title in norm_title:
                    return nid
        return None    


#    def _embed_text(self, texts: List[str]) -> np.ndarray:
    def _embed_text(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
        all_embeddings = []
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                inputs = self.tokenizer(batch, padding=True, truncation=True, max_length=64, return_tensors="pt")
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                all_embeddings.append(embeddings.cpu().numpy())
        return np.vstack(all_embeddings)
#        with torch.no_grad():
#            inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
#            outputs = self.model(**inputs)
#            embeddings = outputs.last_hidden_state.mean(dim=1)
 #           embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
  #      return embeddings.cpu().numpy()

    def _load_graph(self):
        if not os.path.exists(self.graph_path):
            self.graph = nx.Graph()
            print("IT BROKE AT LOAD GRAPH")
        else:
            print("LOAD GRAPHHHHHHHH")
            self.graph = nx.read_gpickle(self.graph_path)

    def _save_graph(self):
        with FileLock(self.graph_lock_path):
            nx.write_gpickle(self.graph, self.graph_path)

    def _build_or_load_faiss(self):
        # Persistent FAISS index files
        principle_index_file = "faiss_principle.index"
        article_index_file = "faiss_article.index"

        # Try to load principle index
        if os.path.exists(principle_index_file):
            self.principle_index = faiss.read_index(principle_index_file)
            # Load ids and texts from graph
            self.principle_ids = []
            self.principle_texts = []
            for nid, data in self.graph.nodes(data=True):
                if data.get("type") == "principle":
                    text = data.get("text")
                    if text:
                        self.principle_ids.append(nid)
                        self.principle_texts.append(text)
        else:
            p_texts, p_ids = [], []
            for nid, data in self.graph.nodes(data=True):
                if data.get("type") == "principle":
                    text = data.get("text")
                    if text:
                        p_texts.append(text)
                        p_ids.append(nid)
            if p_texts:
                p_embeddings = self._embed_text(p_texts)
                self.principle_index = faiss.IndexFlatIP(p_embeddings.shape[1])
                self.principle_index.add(p_embeddings)
                self.principle_ids = p_ids
                self.principle_texts = p_texts
                faiss.write_index(self.principle_index, principle_index_file)
            else:
                self.principle_index = faiss.IndexFlatIP(768)

        # Try to load article index
        if os.path.exists(article_index_file):
            self.article_index = faiss.read_index(article_index_file)
            self.article_ids = []
            self.article_texts = []
            for nid, data in self.graph.nodes(data=True):
                if data.get("type") == "article":
                    text = data.get("text")
                    if text:
                        self.article_ids.append(nid)
                        self.article_texts.append(text)
        else:
            a_texts, a_ids = [], []
            for nid, data in self.graph.nodes(data=True):
                if data.get("type") == "article":
                    text = data.get("text")
                    if text:
                        a_texts.append(text)
                        a_ids.append(nid)
            if a_texts:
                a_embeddings = self._embed_text(a_texts)
                self.article_index = faiss.IndexFlatIP(a_embeddings.shape[1])
                self.article_index.add(a_embeddings)
                self.article_ids = a_ids
                self.article_texts = a_texts
                faiss.write_index(self.article_index, article_index_file)
            else:
                self.article_index = faiss.IndexFlatIP(768)

    def _update_faiss_after_new_nodes(self):
        # Always rebuild and save both indices after new nodes
        principle_index_file = "faiss_principle.index"
        article_index_file = "faiss_article.index"
        p_texts, p_ids = [], []
        a_texts, a_ids = [], []
        for nid, data in self.graph.nodes(data=True):
            if data.get("type") == "principle":
                text = data.get("text")
                if text:
                    p_texts.append(text)
                    p_ids.append(nid)
            elif data.get("type") == "article":
                text = data.get("text")
                if text:
                    a_texts.append(text)
                    a_ids.append(nid)
        # Principle index
        if p_texts:
            p_embeddings = self._embed_text(p_texts)
            self.principle_index = faiss.IndexFlatIP(p_embeddings.shape[1])
            self.principle_index.add(p_embeddings)
            self.principle_ids = p_ids
            self.principle_texts = p_texts
            faiss.write_index(self.principle_index, principle_index_file)
        else:
            self.principle_index = faiss.IndexFlatIP(768)
        # Article index
        if a_texts:
            a_embeddings = self._embed_text(a_texts)
            self.article_index = faiss.IndexFlatIP(a_embeddings.shape[1])
            self.article_index.add(a_embeddings)
            self.article_ids = a_ids
            self.article_texts = a_texts
            faiss.write_index(self.article_index, article_index_file)
        else:
            self.article_index = faiss.IndexFlatIP(768)



    def _semantic_search(self, text: str, node_type: str, top_k=3, threshold=0.75) -> Optional[str]:
        if node_type == "principle":
            index = self.principle_index
            node_ids = self.principle_ids
            texts = self.principle_texts
        else:
            index = self.article_index
            node_ids = self.article_ids
            texts = self.article_texts

        emb = self._embed_text([text])
        D, I = index.search(emb, top_k)

        print(f"\n LLM {node_type}: \"{text}\"")
        for i in range(len(I[0])):
            node_id = node_ids[I[0][i]]
            print(f"    Match {i+1}: \"{texts[I[0][i]]}\" — Score: {D[0][i]:.4f}")

        for score, idx in zip(D[0], I[0]):
            node_id = node_ids[idx]
            if score >= threshold:
                return node_id
        return None



    '''        # OLD VERSION
        #Testing
        print(f"\n LLM article: \"{text}\"")
        for i in range(len(I[0])):
            print(f"    Match {i+1}: \"{self.texts[I[0][i]]}\" — Score: {D[0][i]:.4f}")



        for score, idx in zip(D[0], I[0]):
            if score >= threshold:
                return self.node_ids[idx]
         
        return None
'''

    def _generate_node_id(self, text: str, node_type: str) -> str:
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        timestamp = str(int(time.time()))[-6:]
        return f"{node_type}_{content_hash}_{timestamp}"

    def _call_llm(self, query: str) -> Optional[Dict[str, Any]]:
        prompt = f"""
    You are a legal AI assistant specializing in Indian law. Analyze the following query and provide a structured response.

    Query: {query}

A principle is a foundational legal idea that guides how constitutional rights are interpreted and applied in real-life situations. 
Principles should be formal, objective, and concise, focusing on the intent and scope of the law. 
Use the following examples as a guide for tone and language:

Examples:
- "Establishment of Wards Committees: This principle outlines the constitution of Wards Committees within large municipalities to enable effective governance at a local level."
- "Population Threshold for Wards Committees: This principle sets a population threshold for the implementation of Wards Committees within municipalities, specifically those with a population of over 3 lakhs."
- "Reservation of Seats for Scheduled Castes and Scheduled Tribes: Article 243T mandates the reservation of seats in every Municipality for the Scheduled Castes and Scheduled Tribes. The number of reserved seats is in proportion to their population in the Municipal area."

After listing principles and articles, add a list called "links", where each item is a string in the format "Principle N -> Article X,Y,Z", using the order of the lists above (e.g., "Principle 1 -> Article 2,3", "Principle 2 -> Article 1"). Example: ["Principle 1 -> Article 2,3", "Principle 2 -> Article 1"].

    Please respond with a JSON object containing:
    1. "scenario": {{"example": "A clear description of the legal situation as a scenario"}}
    2. "principles": ["List of relevant legal principles as strings, each following the above tone and format"]
    3. "articles": ["List of HIGHLY relevant constitutional articles from Indian Constution only their descriptions not names"]
    4. "links": ["Principle N -> Article X,Y,Z", ...]
    MAKE SURE The Principles in the links are in same order as the principles list!!!
    Focus on Indian legal framework. Be specific and accurate.
    Dont give anything other than JSON RESPONSE no explaination or anything
    JSON Response:
    """
        try:
        
            client = OpenAI(
                api_key=self.llm_api_key or os.getenv("LLM_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=[
                    {"role": "system", "content": "You are a legal assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            content = response.choices[0].message.content
            start = content.find("{")
            end = content.rfind("}") + 1
            return json.loads(content[start:end])
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None

    def _add_node(self, content: str, node_type: str) -> str:
        node_id = self._generate_node_id(content, node_type)
        data = {
            "type": node_type,
            "auto_generated": True,
            "created_at": int(time.time())
        }

        if node_type == "scenario":
            data["example"] = content
        elif node_type == "principle":
            data["text"] = content
        elif node_type == "article":
            data["title"] = content
            data["layman_summary"] = ""

        self.graph.add_node(node_id, **data)
        return node_id

    def _add_edge_if_missing(self, node1: str, node2: str, edge_type: str):
        if not self.graph.has_edge(node1, node2):
            self.graph.add_edge(node1, node2, type=edge_type)

    def generate_and_insert(self, query: str) -> Dict[str, Any]:
        a = 0
        a1 = []
        p = 0
        p1 = []
        llm_data = self._call_llm(query)
        if not llm_data:
            return {"success": False, "error": "LLM failed."}

        scenario_text = llm_data.get("scenario", {}).get("example", query)
        scenario_id = self._add_node(scenario_text, "scenario")
        addedprincipals = []
        principle_ids = []
        links = llm_data.get("links", [])
        print("ALL LINKS: ",links)

        for principle in llm_data.get("principles", []):
            principle_text = self._normalize_text(principle)
            matched = self._semantic_search(principle_text, "principle", threshold=0.92)  # Increased threshold
            if matched:
                principle_id = matched
            else:
                principle_id = self._add_node(principle_text, "principle")
                if p < len(links):
                    articlestring = links[p]
                else:
                    articlestring = ""
                    print(f"[WARN] No link for principle {p+1}, using empty string as fallback.")
                articlelist = re.findall(r'\b\d+(?:\(\w+\))*', articlestring)
                for i in articlelist:
                    txt = "Article "+str(i)
                    print(txt)
                    articleid = self._find_article_by_number_or_title(txt)
                    print("Articleid my own : ",articleid)
                    if articleid is not None:
                        self._add_edge_if_missing(principle_id, articleid, "explains")
                        print("LINK: ",principle_text,txt)
                p += 1
                p1.append(principle_id)
            principle_ids.append(principle_id)
            self._add_edge_if_missing(scenario_id, principle_id, "supports")

        article_ids = []
        for article in llm_data.get("articles", []):
            article_text = self._normalize_text(article)
            print("Article text is: ", article_text)
            matched = self._find_article_by_number_or_title(article_text)
            if not matched:
                matched = self._semantic_search(article_text, "article")

            if matched:
                article_id = matched
                print("Article through number match",article_id)
                print("matched: ",matched)
            else:
                article_id = self._add_node(article_text, "article")
                a += 1
                a1.append(article_id)
            article_ids.append(article_id)

        # After new nodes, update and persist FAISS indices
        self._update_faiss_after_new_nodes()

        return {
            "success": True,
            "scenario": scenario_id,
            "principles": principle_ids,
            "articles": article_ids,
            "llm_response": llm_data,
            "nodes_created": [f"{a} Article {a1}",f"{p} Principle {p1}"]
        }



 