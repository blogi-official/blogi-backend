from konlpy.tag import Okt

okt = Okt()
text = "두산 오명진 부상KIA-NC 3대3 트레이드 여파"

nouns = okt.nouns(text)
print("[명사 추출 결과]", nouns)
