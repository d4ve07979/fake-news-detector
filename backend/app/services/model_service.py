"""
ModelService — Version finale corrigée
- Lit id2label directement depuis config.json
- Avertit si le texte est en français (modèle anglais uniquement)
- Compatible Transformers 5.x + safetensors
"""
import os, re, json, logging
from typing import Dict, List

logger = logging.getLogger(__name__)

FAKE_PATTERNS = [
    r'\b(BREAKING|URGENT|EXCLUSIVE|SHOCKING)\b',
    r'\b(they don.t want you to know|wake up|sheeple)\b',
    r'\b(mainstream media|deep state)\b',
    r'[!]{2,}',
]


class ModelService:
    def __init__(self):
        self.pipe      = None
        self.is_loaded = False
        self._mock     = False
        self._id2label = {"0": "FAKE", "1": "REAL",
                          "LABEL_0": "FAKE", "LABEL_1": "REAL"}

    def load_model(self, model_path: str):
        abs_path = os.path.abspath(model_path)

        config_path = os.path.join(abs_path, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                raw = cfg.get("id2label", {})
                self._id2label = {}
                for k, v in raw.items():
                    self._id2label[v]            = v
                    self._id2label[f"LABEL_{k}"] = v
                    self._id2label[str(k)]        = v
                logger.info(f"id2label charge : {self._id2label}")
            except Exception as e:
                logger.warning(f"config.json illisible : {e}")
        else:
            logger.warning(f"config.json introuvable : {abs_path}")
            self._mock = True
            self.is_loaded = True
            return

        try:
            from transformers import pipeline
            logger.info(f"Chargement modele : {abs_path}")
            self.pipe = pipeline(
                "text-classification",
                model=abs_path,
                tokenizer=abs_path,
                truncation=True,
                max_length=512,
                device=-1,
            )
            self.is_loaded = True
            logger.info("Modele BERT charge avec succes.")
        except Exception as e:
            logger.error(f"Erreur chargement : {e}")
            self._mock = True
            self.is_loaded = True

    def predict(self, text: str) -> Dict:
        clean = self._preprocess(text)
        is_fr = self._detect_french(clean)

        if self._mock or self.pipe is None:
            return self._mock_predict(clean, is_french=is_fr)

        try:
            res       = self.pipe(clean[:512])[0]
            raw_label = res.get("label", "LABEL_0")
            label     = self._id2label.get(raw_label, raw_label)
            score     = round(float(res.get("score", 0.5)), 4)

            fake_prob = score if label == "FAKE" else round(1.0 - score, 4)
            real_prob = round(1.0 - fake_prob, 4)

            return {
                "label":        label,
                "confidence":   score,
                "fake_prob":    fake_prob,
                "real_prob":    real_prob,
                "keywords":     self._keywords(text),
                "lang_warning": "fr" if is_fr else None,
            }
        except Exception as e:
            logger.error(f"Inference echouee : {e}")
            return self._mock_predict(clean, is_french=is_fr)

    def _preprocess(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'https?://\S+', '[URL]', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _detect_french(self, text: str) -> bool:
        fr_words = {"les","des","une","est","dans","pour","par","sur",
                    "avec","que","qui","pas","ont","ete","cette","son",
                    "ses","leur","leurs","nous","vous"}
        words = set(text.lower().split())
        return len(words & fr_words) >= 3

    def _keywords(self, text: str) -> List[str]:
        found = []
        for p in FAKE_PATTERNS:
            found += re.findall(p, text, re.IGNORECASE)
        return list(set(found))[:5]

    def _mock_predict(self, text: str, is_french: bool = False) -> Dict:
        caps  = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        excl  = text.count('!')
        hits  = sum(len(re.findall(p, text, re.IGNORECASE)) for p in FAKE_PATTERNS)
        score = min(0.95, 0.35 + hits * 0.12 + caps * 0.25 + excl * 0.04)
        label = "FAKE" if score > 0.50 else "REAL"
        conf  = round(score if label == "FAKE" else 1 - score, 4)
        return {
            "label":        label,
            "confidence":   conf,
            "fake_prob":    round(score, 4),
            "real_prob":    round(1 - score, 4),
            "keywords":     self._keywords(text),
            "lang_warning": "fr" if is_french else None,
        }
