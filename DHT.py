import hashlib
import bisect

# -----------------------------
# Hash Function
# -----------------------------
def hash_fn(key):
    return int(hashlib.sha1(key.encode()).hexdigest(), 16)


# -----------------------------
# Node (Peer)
# -----------------------------
class Node:
    def __init__(self, name):
        self.name = name
        self.data = {}

    def store(self, key, value):
        self.data[key] = value

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def lookup(self, key):
        return self.data.get(key, None)


# -----------------------------
# Consistent Hash DHT
# -----------------------------
class ConsistentHashDHT:
    def __init__(self):
        self.nodes = {}
        self.sorted_keys = []

    def add_node(self, node_name):
        node = Node(node_name)
        key = hash_fn(node_name)

        self.nodes[key] = node
        bisect.insort(self.sorted_keys, key)

        print(f"[ADD NODE] {node_name} -> Hash: {key}")

        # Redistribute keys from the next node
        if len(self.sorted_keys) > 1:
            idx = bisect.bisect(self.sorted_keys, key) % len(self.sorted_keys)
            next_node_key = self.sorted_keys[idx]
            if next_node_key != key:
                next_node = self.nodes[next_node_key]
                keys_to_move = []
                # Find keys in next_node that should mathematically belong to the new node
                for k, v in list(next_node.data.items()):
                    if self.get_node(k).name == node_name:
                        keys_to_move.append((k, v))
                
                for k, v in keys_to_move:
                    node.store(k, v)
                    del next_node.data[k]
                    print(f"[REDISTRIBUTE] '{k}' moved to {node.name}")

    def remove_node(self, node_name):
        key = hash_fn(node_name)

        if key not in self.nodes:
            print(f"[ERROR] Node {node_name} not found")
            return

        node = self.nodes.pop(key)
        self.sorted_keys.remove(key)

        print(f"[REMOVE NODE] {node_name}")

        # redistribute data
        for k, v in node.data.items():
            self.insert(k, v)

    def get_node(self, key):
        if not self.sorted_keys:
            return None

        h = hash_fn(key)
        idx = bisect.bisect(self.sorted_keys, h) % len(self.sorted_keys)
        node_key = self.sorted_keys[idx]

        return self.nodes[node_key]

    def insert(self, key, value):
        node = self.get_node(key)
        if node:
            node.store(key, value)
            print(f"[INSERT] '{key}' stored in {node.name}")

    def delete(self, key):
        node = self.get_node(key)
        if node and key in node.data:
            node.delete(key)
            print(f"[DELETE] '{key}' removed from {node.name}")

    def lookup(self, key):
        node = self.get_node(key)
        if node:
            return node.lookup(key)
        return None


# -----------------------------
# P2P Layer
# -----------------------------
class P2PFileSharing:
    def __init__(self, dht):
        self.dht = dht

    def upload(self, file_name, peer_name):
        existing = self.dht.lookup(file_name)

        if existing:
            if peer_name not in existing:
                existing.append(peer_name)
        else:
            self.dht.insert(file_name, [peer_name])

        print(f"[UPLOAD] {file_name} shared by {peer_name}")

    def download(self, file_name):
        peers = self.dht.lookup(file_name)

        if peers:
            print(f"[DOWNLOAD] {file_name} found: {peers}")
            return peers   # ✅ FIXED
        else:
            print(f"[DOWNLOAD] {file_name} not found")
            return None

    def remove_file(self, file_name):
        self.dht.delete(file_name)
        print(f"[REMOVE FILE] {file_name}")