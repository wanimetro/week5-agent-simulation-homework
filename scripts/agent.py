import os
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class Memory:
    fact: str
    source: str

class Agent:
    def __init__(self, name:str, age:int, occupation:str, personality: str, memories=None):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.personality = personality
        
        self.memories:list[Memory] = []
        self.reflections:dict[str, str] = {}

        self.schedule = {}

        if memories:
            for m in memories:
                self.addMemory(Memory(fact=m["fact"], source=m["source"]))
    
    def addMemory(self, memory:Memory):
        self.memories.append(memory)

    def updateRelation(self, target:str, reflection:str):
        self.reflections[target] = reflection

    def setSchedule(self, schedule):
        self.schedule = schedule

    def systemPrompt(self, topic:str|None):
        memory_text = "\n".join([f"- {m.fact} 출처: {m.source}" for m in self.memories])

        if topic:
            topic_text = f"현재 대화 주제: {topic}"
        else:
            topic_text = "현재 정해진 주제는 없습니다. 자신의 기억을 바탕으로 자연스럽게 대화하세요."

        res = [
            f"당신의 이름: {self.name}",
            f"당신의 나이: {self.age}",
            f"당신의 직업: {self.occupation}",
            f"당신의 성격: {self.personality}",
            topic_text,
            "",
            "당신이 알고 있는 기억:",
            memory_text if memory_text else "아직 기억이 없습니다.",
            "",
            "자연스럽게 대화하세요"
        ]
        return "\n".join(res)
    
    def speak(self,prev_conversation:list[dict],topic:str|None,client):
        prev_con="\n".join(
            f"{s['speaker']}:{s['content']}"
            for s in prev_conversation
        )
        user_msg=f"""[지금까지의 대화]
        {prev_con}
        위 대화에 이어서 자연스럽게 한마디 하세요.
        주의:
    자신의 이름을 말하지 마세요.
    이름 접두사(Sowon:, Jin:)를 붙이지 마세요.
    대사만 출력하세요."""

        res=client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role":"system",
                    "content":self.systemPrompt(topic)
                },
                {
                    "role":"user",
                    "content":user_msg
                }
            ],
            temperature=0.7
        )

        saying=res.choices[0].message.content.strip()
        saying = saying.replace(f"{self.name}:","").strip()

        return saying