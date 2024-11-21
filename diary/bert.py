from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F

model_name = "nlptown/bert-base-multilingual-uncased-sentiment"


class BertModel:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)

    def sentiment_analysis(self, sentence):
        inputs = self.tokenizer(
            sentence, return_tensors="pt", padding=True, truncation=True
        )
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs_tensor = F.softmax(outputs.logits, dim=1)
        probs_list = probs_tensor.numpy().flatten().tolist()
        emotion = ["매우 부정", "부정", "중립", "긍정", "매우 긍정"]
        probs = [
            {"name": emotion[i], "pv": round(prob * 100, 2)}
            for i, prob in enumerate(probs_list)
        ]
        # 0: 매우 부정적, 1: 부정적, 2: 중립, 3: 긍정적, 4: 매우 긍정적
        predicted_class = torch.argmax(probs_tensor, dim=-1).item()
        # 예측값, 확률
        return predicted_class, probs
