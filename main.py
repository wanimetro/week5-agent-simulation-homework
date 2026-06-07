import os

from dotenv import load_dotenv
from openai import OpenAI

from Simulation import Simulation

load_dotenv()

if __name__ == "__main__":

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    sim = Simulation(client=client)
    sim.runSimulation()