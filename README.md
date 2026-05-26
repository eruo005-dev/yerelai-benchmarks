# yerelai-benchmarks

> Türkçe LLM benchmark sonuçları için **açık veri deposu**.
> Site: [yerelai-site.vercel.app/benchmark](https://yerelai-site.vercel.app/benchmark)

Her satır = bir model × bir donanım × bir kuantizasyon × bir veri sürümü × bir kişi.
Hiçbir ölçüm güven listesinde olmadan yayınlanmaz. PR\'ler beklenir.

## Lisans

Tüm veriler **CC-BY-4.0** — atıfla serbestçe kullan, paylaş, fork at.
Test scriptleri **MIT**.

## Hangi suiteleri çalıştırıyoruz?

| Suite | Tür | Veri | Skor |
|---|---|---|---|
| **TR-MMLU** | Multi-choice (9 ders, KOC-CS) | [Bayram et al. 2025](https://arxiv.org/abs/2407.12402) | 0–100 % |
| **TurkBench** | 21 alt-görev | [TURKBench HF](https://huggingface.co/datasets/TURKBench) | 0–100 % |
| **MMLU-Pro-TR** | 10-şıklı | [malhajar/mmlu-pro-tr](https://huggingface.co/datasets/malhajar/mmlu-pro-tr) | 0–100 % |
| **KPSS Genel** | ÖSYM 2018-2024 | bu repo | 0–100 % |
| **TUS Klinik** | ÖSYM 2019-2024 | bu repo | 0–100 % |
| **IFEval-TR** | Talimat takibi | bu repo | 0–100 % |
| **HumanEval-TR** | Kod pass@1 | bu repo | 0–100 % |
| **Hallucination-TR** | TruthfulQA-TR | bu repo | 0–100 % |
| **E-ticaret-TR** | 3-hakem insan eval | bu repo (özel) | 0–100 % |
| **Hukuki-TR** | 2-avukat insan eval | bu repo (özel) | 0–100 % |
| **TPS** | Token/sn benchmark | n/a (hardware-bound) | tok/s |
| **Cost-per-1M-TR** | Modeled — ölçüm değil | hesaplama | TRY |

## Yapı

```
yerelai-benchmarks/
├── README.md                ← bu dosya
├── LICENSE                  ← CC-BY-4.0
├── data/
│   ├── runs.jsonl           ← canonical run kayıtları (append-only)
│   ├── dimensions.json
│   └── hardware.json
├── scripts/
│   ├── run-tr-mmlu.py       ← lm-evaluation-harness wrapper
│   ├── run-tps.py           ← token/saniye ölçer
│   ├── run-ifeval-tr.py
│   ├── verify-submission.py ← PR CI bot
│   └── requirements.txt
├── tasks/
│   └── turkishmmlu/         ← lm-eval task yaml'ları
├── prompts/
│   ├── ifeval-tr/           ← talimat takibi prompt seti
│   └── hallucination-tr/
└── runs/                    ← raw log dökümü (PR'larla biriken)
    └── 2026-05-24-trendyol-asure-12b-tr-mmlu-rtx3080/
        ├── run.log
        ├── results.json
        └── reproduce.sh
```

## Bir koşu nasıl katkı verirsin?

### 1) Ortam hazırla
```bash
git clone https://github.com/eruo005-dev/yerelai-benchmarks.git
cd yerelai-benchmarks
pip install -r scripts/requirements.txt
```

### 2) Bir suite çalıştır (örnek: TR-MMLU)
```bash
# Önce Ollama'da modelini hazırla
ollama pull alibayram/Trendyol-LLM-Asure-12B

# Sonra:
python scripts/run-tr-mmlu.py \
    --model "alibayram/Trendyol-LLM-Asure-12B" \
    --runtime ollama-0.6 \
    --quant q4_k_m \
    --hardware rtx-3080-10gb \
    --seed 42 \
    --output runs/$(date +%Y-%m-%d)-asure-rtx3080.json
```

### 3) PR aç
- `data/runs.jsonl`'a tek bir JSON satır ekle
- `runs/...` altında raw log + results.json + reproduce.sh koy
- PR aç. CI `scripts/verify-submission.py` ile doğrular.
- Mevcut bir kayıtla aynı setup ±5 puan içindeyse → otomatik **verified** badge.

## Şu anki durum (2026-05-26)

- **11 ölçüm** (Trendyol-Asure 12B + GPT-4o + Claude 3.5 Sonnet + 3 community)
- **4 boyut populated** (TR-MMLU, TPS, Cost, IFEval-TR)
- **2 ölçüm verified** (GPT-4o + Sonnet cross-confirm)
- Hedef: Eylül 12'ye 200+ ölçüm × 30+ model

## İletişim

- Site: [yerelai-site.vercel.app](https://yerelai-site.vercel.app)
- Issue: bu repo
- Founding: [yerelai-site.vercel.app/founding](https://yerelai-site.vercel.app/founding)
