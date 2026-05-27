from abc import ABC, abstractmethod

class AIPlatform(ABC):
    

    @abstractmethod
    def chat(self, prompt: str)-> str:
        """sends a prompt to the ai and returns the response"""
        pass