from scripts.agent import Agent

AGENTS={
    "Sowon":Agent(
        name="Sowon",
        age=22,
        occupation="대학생",
        personality="노래를 듣는 것을 좋아해서 콘서트를 자주 간다.",
        memories=[
            {"fact":"콘서트에서 영상을 찍기 위해 카메라를 자주 대여한다.", "source":"Sowon"}
        ]
    ),
    "Seojun":Agent(
        name="Seojun",
        age=25,
        occupation="회사원",
        personality="신중하고 거래 안전을 중요시한다",
        memories=[
            {"fact":"중고거래 경험이 많다", "source":"Seojun"}
        ]
    ),
    "Sujin":Agent(
        name="Sujin",
        age=28,
        occupation="주부",
        personality="적극적이고 활발함",
        memories=[
            {"fact":"부업으로 대여사이트에 대여물건들을 올려 돈을 번다", "source":"Sujin"}
        ]
    ),
    "Jin": Agent(
        name="Jin",
        age=30,
        occupation="창업 준비생",
        personality="아이디어가 많고 적극적",
        memories=[
            {
                "fact":"대여 플랫폼 사업을 구상 중이다",
                "source":"Jin"
            }
        ]
    )
}

SPACES = [
    "콘서트 팬 커뮤니티",
    "당근 채팅방",
    "번개장터 거래방",
    "대여 판매자 커뮤니티",
    "HARUMAN 웹사이트"
]