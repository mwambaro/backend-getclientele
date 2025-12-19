from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import numpy as np

# optional backends: FAISS local or Milvus remote
USE_MILVUS = os.getenv('VECTOR_BACKEND', 'faiss') == 'milvus'

app = FastAPI(title='Vector Search Service')

class Doc(BaseModel):
    id: str
    name: Optional[str] = ''
    description: Optional[str] = ''

class IndexRequest(BaseModel):
    docs: List[Doc]

class QueryRequest(BaseModel):
    q: str
    top_k: Optional[int] = 10

# lazy import of heavy libs
_model = None
_index = None
_ids = []


def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(os.getenv('EMBED_MODEL', 'all-MiniLM-L6-v2'))
    return _model


def _ensure_faiss_index(dim):
    global _index
    import faiss
    if _index is None:
        _index = faiss.IndexFlatIP(dim)
    return _index


@app.post('/index')
async def index(req: IndexRequest):
    model = _load_model()
    texts = [(d.name or '') + ' ' + (d.description or '') for d in req.docs]
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    if USE_MILVUS:
        # minimal Milvus insertion (assumes collection exists)
        from pymilvus import Collection, connections
        host = os.getenv('MILVUS_HOST', 'localhost')
        port = int(os.getenv('MILVUS_PORT', '19530'))
        connections.connect(host=host, port=port)
        coll_name = os.getenv('MILVUS_COLLECTION', 'getclientele_products')
        c = Collection(coll_name)
        # assume schema [id:str, embedding: vector<float>]
        entities = [ [d.id for d in req.docs], embs.tolist() ]
        c.insert(entities)
        return {'inserted': len(req.docs)}
    else:
        idx = _ensure_faiss_index(embs.shape[1])
        # expand in-memory index (note: IndexFlatIP doesn't support delete; simple approach)
        idx.add(embs.astype(np.float32))
        # store ids
        _ids.extend([d.id for d in req.docs])
        return {'inserted': len(req.docs)}


@app.post('/query')
async def query(req: QueryRequest):
    model = _load_model()
    q_emb = model.encode([req.q], convert_to_numpy=True, normalize_embeddings=True)
    top_k = min(int(req.top_k or 10), 100)
    if USE_MILVUS:
        from pymilvus import Collection, connections
        host = os.getenv('MILVUS_HOST', 'localhost')
        port = int(os.getenv('MILVUS_PORT', '19530'))
        connections.connect(host=host, port=port)
        coll_name = os.getenv('MILVUS_COLLECTION', 'getclientele_products')
        c = Collection(coll_name)
        # do a simple search; assume embedding field name 'embedding'
        results = c.search(q_emb.tolist(), anns_field='embedding', param={'metric_type': 'IP'}, limit=top_k)
        items = []
        for res in results[0]:
            items.append({'id': res.id, 'score': float(res.score)})
        return {'items': items}
    else:
        import faiss
        global _index, _ids
        if _index is None or len(_ids) == 0:
            return {'items': []}
        D, I = _index.search(q_emb.astype(np.float32), top_k)
        items = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx < 0 or idx >= len(_ids):
                continue
            items.append({'id': _ids[idx], 'score': float(score)})
        return {'items': items}


@app.get('/health')
async def health():
    return {'status': 'ok', 'backend': 'milvus' if USE_MILVUS else 'faiss'}
