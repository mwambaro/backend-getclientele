import time
import random
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = 'all-MiniLM-L6-v2'
NUM_DOCS = int(1e4)
BATCH = 256

model = SentenceTransformer(MODEL_NAME)

# synthetic dataset
texts = [f"product {i} description " + " sample text" * random.randint(1,10) for i in range(NUM_DOCS)]

start = time.time()
embs = []
for i in range(0, NUM_DOCS, BATCH):
    batch_texts = texts[i:i+BATCH]
    emb = model.encode(batch_texts, convert_to_numpy=True)
    embs.append(emb)
embs = np.vstack(embs)
print('Embedding generation time:', time.time() - start)

# simple similarity query benchmark
query = 'comfortable kids shoes'
q_emb = model.encode([query], convert_to_numpy=True)
start = time.time()
# naive dot-product search
scores = embs @ q_emb[0]
best = np.argsort(-scores)[:10]
print('Query time (naive):', time.time() - start)
print('Top ids:', best[:5])
