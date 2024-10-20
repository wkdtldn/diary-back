from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Pre-trained BERT 모델과 토크나이저를 로드 (여기서는 한국어 BERT 모델을 사용)
model_name = "beomi/kcbert-base"


class BertModel:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)

    def sentiment_analysis(self, sentence):
        # 문장 토큰화
        inputs = self.tokenizer(
            sentence, return_tensors="pt", padding=True, truncation=True
        )

        # 모델 예측 모드로 전환 후 로짓 값 얻기
        self.model.eval()

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        # 로짓 값을 확률로 변환
        probs = torch.nn.functional.softmax(logits, dim=-1)

        # 클래스 예측 (0: 부정, 1: 중립, 2: 긍정)
        predicted_class = torch.argmax(probs, dim=-1).item()

        if predicted_class == 0:
            emotion = "부정"
        elif predicted_class == 1:
            emotion = "중립"
        else:
            emotion = "긍정"
        print(f"예측된 감정: {emotion}, 확률: {probs}")
