# ml

Own palm-vein matcher (CNN embedding). Not started — see README.md → Roadmap → Phase 6.

Planned layout:
- `capture/` — pull 240×320 NIR JPEGs from the AI10 over UART (`0x71`), tag by user/session/hand.
- `roi/` — finger-valley keypoints → normalised square crop.
- `train/` — Kaggle notebooks: MobileNet-class backbone, triplet/ArcFace loss, pre-train on CASIA/PolyU, fine-tune on our set.
- `eval/` — ROC, EER, FAR@FRR.
- `deploy/` — INT8 quantisation, ESP-DL export.

Training runs on Kaggle GPUs only.
