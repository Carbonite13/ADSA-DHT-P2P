from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from DHT import ConsistentHashDHT, P2PFileSharing, hash_fn

app = Flask(__name__)
CORS(app)

# Initialize
dht = ConsistentHashDHT()
p2p = P2PFileSharing(dht)

# Initial nodes
dht.add_node("Peer1")
dht.add_node("Peer2")
dht.add_node("Peer3")


# -----------------------------
# Home
# -----------------------------
@app.route('/')
def home():
    # return "DHT Backend Running ✅"
    return render_template("index.html")


# -----------------------------
# Upload
# -----------------------------
@app.route('/upload', methods=['POST'])
def upload():
    print('uploading')
    data = request.json
    p2p.upload(data['file'], data['peer'])
    return jsonify({"message": "Uploaded"})


# -----------------------------
# Download
# -----------------------------
@app.route('/download', methods=['GET'])
def download():
    print('downloading')
    file = request.args.get('file')
    peers = p2p.download(file)
    return jsonify({"peers": peers})


# -----------------------------
# Delete File
# -----------------------------
@app.route('/delete', methods=['POST'])
def delete():
    print('deleting')
    data = request.json
    p2p.remove_file(data['file'])
    return jsonify({"message": "Deleted"})


# -----------------------------
# Add Node
# -----------------------------
@app.route('/add_node', methods=['POST'])
def add_node():
    print('add node')
    name = request.json['name']
    dht.add_node(name)
    return jsonify({"message": "Node added"})


# -----------------------------
# Remove Node
# -----------------------------
@app.route('/remove_node', methods=['POST'])
def remove_node():
    print('remove node')
    name = request.json['name']
    dht.remove_node(name)
    return jsonify({"message": "Node removed"})


# -----------------------------
# State
# -----------------------------
@app.route('/state', methods=['GET'])
def state():
    print('state')
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
    return jsonify(result)


# -----------------------------
# Run
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)