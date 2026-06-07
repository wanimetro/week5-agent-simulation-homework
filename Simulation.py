from config.preset import AGENTS
from openai import OpenAI
from scripts.agent import Memory
import os
import json

class Simulation:

    def __init__(self, client: OpenAI):

        self.agents = AGENTS
        self.client = client

        self.space = [
            "콘서트 팬 커뮤니티",
            "당근 채팅방",
            "번개장터 거래방",
            "대여 판매자 커뮤니티",
            "HARUMAN 웹사이트"
        ]

        self.time_slots = [
            "08:00",
            "10:00",
            "12:00",
            "14:00",
            "16:00",
            "18:00",
            "20:00"
        ]

    def generatePlans(self):

        for agent in self.agents.values():
            print(f"{agent.name} 계획 생성 시작")
            memories = "\n".join(
                [m.fact for m in agent.memories]
            )

            prompt = f"""
    당신은 다음 Agent입니다.

    이름: {agent.name}
    나이: {agent.age}
    직업: {agent.occupation}
    성격: {agent.personality}

    기억:
    {memories}

    가능한 활동 공간:
    - 콘서트 팬 커뮤니티
    - 당근 채팅방
    - 번개장터 거래방
    - 대여 판매자 커뮤니티
    - HARUMAN 웹사이트

    08:00 ~ 20:00까지
    시간대별 계획을 세우세요.

    반드시 JSON만 출력하세요.
    설명 금지. 코드블록 금지

    예시:

    {{
    "08:00":"콘서트 팬 커뮤니티",
    "10:00":"HARUMAN 웹사이트",
    "12:00":"당근 채팅방",
    "14:00":"HARUMAN 웹사이트",
    "16:00":"콘서트 팬 커뮤니티",
    "18:00":"HARUMAN 웹사이트",
    "20:00":"대여 판매자 커뮤니티"
    }}
    """

            response = self.client.chat.completions.create(
                model=os.getenv("MODEL"),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8
            )

            print("FACT RESPONSE:")
            print(response.choices[0].message.content)

            schedule_text = response.choices[0].message.content

            try:

                schedule = json.loads(schedule_text)

                agent.setSchedule(schedule)

                print(f"\n[{agent.name} 계획 생성 완료]")
                print(schedule)

            except Exception as e:

                print(f"\n[{agent.name}] 계획 생성 실패")
                print(schedule_text)

                raise e

    def runSimulation(self):

        for day in range(1, 3):

            print(f"\n{'='*20}")
            print(f"DAY {day}")
            print(f"{'='*20}")

            self.generatePlans()

            for time in self.time_slots:

                print(f"\n===== {time} =====")

                location_map = {}

                for agent in self.agents.values():

                    location = agent.schedule[time]

                    print(agent.name,"->",location)

                    if location not in location_map:
                        location_map[location] = []

                    location_map[location].append(agent)
                
                print("\n[같은 공간 그룹]")


                for location, agents in location_map.items():
                    names = [agent.name for agent in agents]
                    print(location, ":", names)

                for location, agents in location_map.items():
                    if len(agents) >= 2:
                        print(f"\n[대화 발생] {location}")

                        self.runConversation(agents=agents,location=location,turns=4)
        self.saveReport("Sowon")

    
    def saveFacts(self, agents, facts):

        for fact in facts:

            for agent in agents:

                agent.addMemory(
                    Memory(
                        fact=fact,
                        source="conversation"
                    )
                )

    def runConversation(self,agents,location,turns=4):

        community_prompt = {
        "HARUMAN 웹사이트":
            "물건 대여를 원하는 사람과 대여 판매자가 대화한다. 직거래로 할지 택배거래로 할지, 하루당 대여료, 보증금 등을 이야기한다.",

        "당근 채팅방":
            "중고물품 구매와 판매 대화를 한다. 판매자가 물건을 올리면 구매자가 구매의사를 밝히며 직거래장소, 가격 흥정 등을 이야기해야하며 그 외 이야기는 하지 않는다. 물건대여가 아닌 물건 구매에 관한 이야기만 해야한다.",

        "번개장터 거래방":
            "중고거래 중심으로 가격흥정과 거래약속을 한다. 물건을 대여하는 것이 아닌, 중고물건을 직접 구매만 해야한다",

        "콘서트 팬 커뮤니티":
            "가수, 아이돌, 콘서트, 팬활동 이야기를 한다.",

        "대여 판매자 커뮤니티":
            "대여사업 운영, 물품관리, 파손, 보증금 이야기를 한다."
}
        
        topic = community_prompt[location]

        conversation = []

        print(f"\n=== 대화 시작 ({location}) ===")

        for i in range(turns):

            speaker = agents[i % len(agents)]

            saying = speaker.speak(
                prev_conversation=conversation,
                topic=topic,
                client=self.client
            )

            conversation.append({
                "speaker": speaker.name,
                "content": saying
            })

            print(
                f"{speaker.name}: {saying}"
            )

        facts = self.extractFacts(conversation)
        self.saveFacts(agents, facts)
        self.updateReflections(agents,conversation)

        print("\n[추출된 Fact]")
        print(facts)

        return conversation
       

    def extractFacts(self, conversation):

        text = "\n".join(
            f"{c['speaker']}:{c['content']}"
            for c in conversation
        )

        prompt = f"""
    다음 대화에서 중요한 사실(Fact)만 추출하세요.

    {text}

    반드시 JSON 배열만 출력하세요.
    설명 금지.
    코드블록 금지.
    다른 텍스트 금지.

    [
    "Sowon은 카메라를 자주 대여한다",
    "Jin은 대여 플랫폼 창업을 준비한다"
    ]
    """
        
        response = self.client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            temperature=0
        )

        facts_text = response.choices[0].message.content

        facts_text = facts_text.replace(
            "```json",
            ""
        )

        facts_text = facts_text.replace(
            "```",
            ""
        )

        facts_text = facts_text.strip()
        facts = json.loads(facts_text)
        return facts



    def updateReflections(self, agents, conversation):
        for agent in agents:

            others = [
                a.name
                for a in agents
                if a.name != agent.name
            ]

            prompt = f""" 다음 대화를 보고
                    {agent.name} 관점에서
                    {others}에 대한 관계를 한 문장으로 요약하세요.
                    {conversation}"""
            response = self.client.chat.completions.create(
                model=os.getenv("MODEL"),
                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                    ],
                temperature=0)

            reflection = response.choices[0].message.content
            for other in others:
                agent.updateRelation(other, reflection)


    def saveReport(self, target_name):

        target = self.agents[target_name]

        with open(
            f"{target_name}_report.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(f"=== {target_name} REPORT ===\n\n")

            f.write("=== MEMORY ===\n")

            for memory in target.memories:

                f.write(
                    f"- {memory.fact} "
                    f"(source: {memory.source})\n"
                )

            f.write("\n=== REFLECTIONS ===\n")

            for person, relation in target.reflections.items():

                f.write(f"\n[{person}]\n")
                f.write(f"{relation}\n")

        print(
            f"\n{target_name}_report.txt 저장 완료"
        )