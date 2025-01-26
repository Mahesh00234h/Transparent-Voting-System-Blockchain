import hashlib
import json
from typing import Dict, List

class VoterRegistry:
    def __init__(self, filename="voters.json"):
        self.filename = filename
        self.voters = {}
        self.voted = []
        self.load_registry()

    def save_registry(self):
        with open(self.filename, "w") as file:
            json.dump({"voters": self.voters, "voted": self.voted}, file, indent=4)

    def load_registry(self):
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                self.voters = data.get("voters", {})
                self.voted = data.get("voted", [])
        except FileNotFoundError:
            self.voters = {}
            self.voted = []

    def register_voter(self, voter_id: str, name: str, age: int):
        if voter_id in self.voters:
            return {"success": False, "message": "Voter ID already exists."}
        if age < 18:
            return {"success": False, "message": "Voter must be at least 18 years old."}

        self.voters[voter_id] = {
            "name": name,
            "age": age,
            "voter_hash": self.generate_voter_hash(voter_id, name),
        }
        self.save_registry()
        return {"success": True, "message": "Voter registered successfully."}

    def generate_voter_hash(self, voter_id: str, name: str) -> str:
        data = f"{voter_id}-{name}"
        return hashlib.sha256(data.encode()).hexdigest()

    def authenticate_voter(self, voter_id: str):
        if voter_id not in self.voters:
            return {"success": False, "message": "Voter ID not found."}
        if voter_id in self.voted:
            return {"success": False, "message": "Voter has already cast their vote."}
        return {"success": True, "message": "Voter authenticated successfully."}

    def mark_voted(self, voter_id: str):
        if voter_id in self.voted:
            return {"success": False, "message": "Voter has already voted."}
        self.voted.append(voter_id)
        self.save_registry()
        return {"success": True, "message": "Vote successfully recorded for the voter."}

    def get_all_voters(self):
        return [{"voter_id": voter_id, **voter} for voter_id, voter in self.voters.items()]
