from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict

from DHT import ConsistentHashDHT, P2PFileSharing, hash_fn

app = FastAPI(title="DHT & P2P Simulator", description="High-performance simulation of a Consistent Hash DHT.")

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
dht = ConsistentHashDHT()
p2p = P2PFileSharing(dht)

# Initial nodes to populate the network
dht.add_node("Peer1")
dht.add_node("Peer2")
dht.add_node("Peer3")

# -----------------------------
# Models
# -----------------------------
class NodeRequest(BaseModel):
    name: str

class FileUploadRequest(BaseModel):
    file: str
    peer: str

class FileDeleteRequest(BaseModel):
    file: str

class FileInfo(BaseModel):
    name: str
    angle: float

class NodeInfo(BaseModel):
    angle: float
    files: List[FileInfo]

# -----------------------------
# Endpoints
# -----------------------------

@app.get("/")
async def root():
    return {"status": "DHT API Running 🌌", "version": "2.0"}

@app.post("/upload")
async def upload(request: FileUploadRequest):
    p2p.upload(request.file, request.peer)
    return {"message": f"File '{request.file}' shared by '{request.peer}'"}

@app.get("/download")
async def download(file: str = Query(..., description="The name of the file to lookup")):
    peers = p2p.download(file)
    if peers is None:
        raise HTTPException(status_code=404, detail=f"File '{file}' not found in the network.")
    return {"file": file, "peers": peers}

@app.post("/delete")
async def delete_file(request: FileDeleteRequest):
    p2p.remove_file(request.file)
    return {"message": f"File '{request.file}' removed from the DHT."}

@app.post("/add_node")
async def add_node(request: NodeRequest):
    dht.add_node(request.name)
    return {"message": f"Node '{request.name}' joined the network."}

@app.post("/remove_node")
async def remove_node(request: NodeRequest):
    dht.remove_node(request.name)
    return {"message": f"Node '{request.name}' left the network."}

@app.get("/state", response_model=Dict[str, NodeInfo])
async def get_state():
    # max_hash for SHA-1 is 2^160 - 1
    max_hash = 2**160 - 1
    result = {}
    
    for key in dht.sorted_keys:
        node = dht.nodes[key]
        node_angle = (key / max_hash) * 360
        
        file_list = []
        for f in node.data.keys():
            f_hash = hash_fn(f)
            f_angle = (f_hash / max_hash) * 360
            file_list.append({"name": f, "angle": f_angle})
            
        result[node.name] = {
            "angle": node_angle,
            "files": file_list
        }
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
