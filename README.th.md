# 🌐 hookglot

> Hooks สำหรับแปลภาษาใน Claude Code — ลดการเผา Token สำหรับ non-English users 60-80%

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://claude.com/claude-code)
[![Cross-platform](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#)
[![Version](https://img.shields.io/badge/version-1.2.0-success.svg)](CHANGELOG.md)

**hookglot** จะดักจับ prompt ที่ส่งไป/กลับจาก Claude Code และแปลภาษาให้โดยอัตโนมัติผ่านผู้ให้บริการ LLM ที่เลือก — ทั้งแบบรันในเครื่อง (Ollama) หรือคลาวด์ (รองรับ 9 ค่าย) ลดการเผา Token สำหรับ non-English users 60-80%

📖 **Read in English**: [README.md](README.md)

---

## ✨ คุณสมบัติเด่น (Features)

- 🎯 **2 วิธีการแปล** — แปลเฉพาะขาเข้า (input-only) หรือแปลเฉพาะขาออก (output-only) (พร้อมโหมดปิดการใช้งาน)
- 🌏 **รองรับ 8 ภาษาเอเชีย** — ไทย, ญี่ปุ่น, จีน (ตัวย่อ/ตัวเต็ม), เกาหลี, เวียดนาม, อินโดนีเซีย, มาเลย์
- 🤖 **ผู้ให้บริการแปลภาษา 9 แห่ง** — Ollama (ค่าเริ่มต้น, ฟรี), OpenAI, Anthropic, Google, DeepSeek, Alibaba, Moonshot, Zhipu, NVIDIA
- 🛡️ **รักษาฟอร์แมตอย่างชาญฉลาด** — บล็อกโค้ด (code blocks), URLs, IP, ตัวแปร environment จะไม่ถูกแก้ไขหรือเพี้ยนไปจากการแปล
- 🎮 **คำสั่ง Slash Commands** — สลับการตั้งค่าได้โดยไม่ต้องออกจาก Claude Code (`/hookglot-method`, `/hookglot-translator`, `/hookglot-off`, ฯลฯ)
- 🔒 **เน้นความเป็นส่วนตัว (Privacy-First)** — Ollama เก็บข้อมูลทุกอย่างไว้ในเครื่องคุณเท่านั้น
- ✅ **ติดตั้งปลอดภัย** — ไม่กระทบ hooks, หน่วยความจำ (memory), และ slash commands เดิมของ Claude Code ที่คุณมีอยู่

[https://github.com/user-attachments/assets/797a709a-982b-44be-acfe-37810cda16b3](https://github.com/user-attachments/assets/797a709a-982b-44be-acfe-37810cda16b3)

---

## 🎬 หลักการทำงาน

```
วิธีที่ 1 (แปลเฉพาะขาเข้า - Input-only) ⭐ แนะนำ
   Prompt ภาษาไทย ──► [hook แปลเป็น → ภาษาอังกฤษ] ──► Claude
                                                       │
   คำตอบภาษาไทย ◄──────────────────────────────────────┘ (Claude ตอบกลับเป็นภาษาไทยโดยตรง)

วิธีที่ 2 (แปลเฉพาะขาออก - Output-only)
   Prompt ภาษาไทย ────────────────────────────────► Claude (Master Prompt บังคับให้ Claude ตอบอังกฤษ)
                                                       │
   ภาษาอังกฤษ + คำแปล ◄── [hook ทำการแปล] ◄────────────┘
```

---

## 🚀 เริ่มต้นใช้งานด่วน

### การติดตั้ง

**macOS / Linux:**
```bash
git clone https://github.com/dai4uoy/hookglot.git
cd hookglot
pip install -e .
hookglot install
```

**Windows (CMD หรือ PowerShell):**
```bat
git clone https://github.com/dai4uoy/hookglot.git
cd hookglot
python -m pip install -e .
python -m hookglot install
```

ตัวติดตั้งจะทำขั้นตอนดังนี้:
1. เลือกภาษา (ไทย, ญี่ปุ่น, จีน, เกาหลี ฯลฯ)
2. เลือกวิธีการแปล (ขาเข้า หรือ ขาออก)
3. เลือกผู้ให้บริการแปลภาษา (Ollama, DeepSeek, OpenAI ฯลฯ)
4. ตั้งค่า API key (หากเลือกผู้ให้บริการคลาวด์)
5. (ทางเลือก) ระบุชื่อโมเดลที่ต้องการ (หรือใช้ค่าเริ่มต้น)


### การใช้งานครั้งแรก

```bash
hookglot test         # ทดสอบว่าระบบแปลทำงานได้ปกติ
claude                # ใช้งาน Claude Code ตามปกติ — การแปลจะทำงานอัตโนมัติ
```

---

## 🎮 คำสั่ง Slash Commands (ภายใน Claude Code)

หลังติดตั้ง คุณสามารถใช้คำสั่งเหล่านี้ใน `claude` ได้ทันที:

| คำสั่ง | คำอธิบาย |
|--------ขขขขขขขขขขขขขขขขขข-|-----------------------------------------|
| `/hookglot-status`          | แสดงการตั้งค่าปัจจุบัน                       |
| `/hookglot-method 1`        | เปลี่ยนเป็นโหมดแปลเฉพาะขาเข้า               |
| `/hookglot-method 2`        | เปลี่ยนเป็นโหมดแปลเฉพาะขาออก              |
| `/hookglot-off`             | ปิดการใช้งาน hookglot ชั่วคราว               |
| `/hookglot-translator kimi` | เปลี่ยนผู้ให้บริการแปลภาษา                   |
| `/hookglot-lang th`         | เปลี่ยนภาษาเป้าหมาย (เช่น เป็นภาษาไทย)       |
| `/hookglot-test`            | ทดสอบระบบการแปล                        | 

หลังจากการเปลี่ยนการตั้งค่าใดๆ ให้พิมพ์ `/clear` เพื่อเริ่มเซสชันใหม่ให้การตั้งค่ามีผลบังคับใช้

---

## 🛠️ คำสั่งผ่าน Terminal (CLI)

```bash
hookglot install              # ตั้งค่าแบบ Interactive
hookglot status               # แสดงการตั้งค่าปัจจุบัน
hookglot switch 1|2|off       # สลับวิธีการแปลหรือปิดการใช้งาน
hookglot translator <name>    # เปลี่ยนผู้ให้บริการแปลภาษา
hookglot lang <code>          # เปลี่ยนภาษา
hookglot set-key <provider>   # ตั้งค่า API key
hookglot test                 # ทดสอบการแปล
hookglot uninstall            # ถอนการติดตั้ง hookglot (ไม่กระทบการตั้งค่าอื่น)
```

---

## 🌍 ภาษาที่รองรับ

| รหัส    | ภาษา           | ภาษาท้องถิ่น       |
|---------|----------------|------------------|
| `th`    | Thai           | ภาษาไทย          |
| `ja`    | Japanese       | 日本語            |
| `zh-CN` | Chinese (Simp) | 简体中文          |
| `zh-TW` | Chinese (Trad) | 繁體中文          |
| `ko`    | Korean         | 한국어            |
| `vi`    | Vietnamese     | Tiếng Việt       |
| `id`    | Indonesian     | Bahasa Indonesia |
| `ms`    | Malay          | Bahasa Melayu    |

---

## 🛡️ การรับประกันความปลอดภัยเมื่อติดตั้ง

hookglot ถูกออกแบบมาให้อยู่ร่วมกับการตั้งค่า Claude Code เดิมของคุณได้:

- **Hooks เดิมของคุณจะยังอยู่ครบ** — การติดตั้ง hookglot จะ *ไม่* เขียนทับ hooks ที่คุณมีอยู่แล้วสำหรับ `Stop`, `UserPromptSubmit`, หรือ event อื่นๆ แต่มันจะทำงานควบคู่กันไป
- **ข้อมูล memory ใน `CLAUDE.md` จะยังอยู่ครบ** — hookglot ใช้เครื่องหมายระบุตำแหน่ง (`` ... ``) จึงปรับแก้เฉพาะบล็อกของตัวเองเท่านั้น
- **คำสั่ง slash commands อื่นๆ ของคุณจะยังอยู่ครบ** — การถอนการติดตั้งจะลบแค่ไฟล์ `hookglot-*.md` โดยไม่ยุ่งกับคำสั่ง custom เดิมที่คุณสร้างไว้

---

## 📂 การตั้งค่า Claude ระดับโปรเจกต์ (Project-Level)

Claude Code อนุญาตให้แต่ละโปรเจกต์มีไฟล์ `.claude/settings.json` เป็นของตัวเอง ซึ่งจะทับซ้อน (override) การตั้งค่าระดับ Global ได้ หากคุณมีไฟล์นี้ hookglot แบบ Global จะไม่ทำงานในโปรเจกต์นั้น

เมื่อคุณรัน `hookglot install` หรือ `hookglot switch` ตัว hookglot จะตรวจสอบและแสดงโค้ดที่คุณสามารถนำไปใส่ใน settings ของโปรเจกต์ได้:

```
⚠️  ตรวจพบการตั้งค่าระดับโปรเจกต์:
     /path/to/project/.claude/settings.json

   หาก hookglot ไม่ทำงานในโปรเจกต์นี้ ให้นำโค้ดด้านล่างไปใส่ในไฟล์ดังกล่าว
   ตรงส่วน "hooks" → "Stop":

     {
       "hooks": {
         "Stop": [{
           "hooks": [{
             "type": "command",
             "command": "/your/python -m hookglot.hooks.translate_output",
             "timeout": 90
           }]
         }]
       }
     }
```

โค้ดแนะนำนี้จะใช้ path ของ Python ในเครื่องคุณจริงๆ มาให้เลย (ไม่ต้องแก้เอง)

---

## 🛡️ Format Preservation

hookglot ใช้ระบบป้องกันฟอร์แมต 3 ชั้น เพื่อให้เนื้อหาทางเทคนิคไม่ผิดเพี้ยนไปจากการแปล:

1. **ดึง Code Block ออกมา (Extraction)** — ป้องกันเนื้อหาใน \`\`\`code\`\`\` และ \`inline\` ไม่ให้ถูกแปล
2. **ป้องกันองค์ประกอบสำคัญ (Aggressive Element Protection)** — URLs, IP, อีเมล, ตัวแปร env, path ของไฟล์, รหัสแฮช, และค่าคงที่ต่างๆ จะไม่ถูกแก้ไข
3. **คำสั่งควบคุมการแปลที่เข้มงวด (Strict Translator Prompts)** — มีคำสั่งเฉพาะเพื่อให้โมเดลคงโครงสร้าง Markdown ไว้ดังเดิม

ผลลัพธ์: ความแม่นยำในการรักษาฟอร์แมตประมาณ 90-95% สำหรับการใช้งานทั่วไป

---

## 📚 เอกสารอ้างอิง
 
- [**Methods**](docs/methods.md)                  — ควรเลือกใช้ท่าแบบไหนและเมื่อไหร่
- [**Providers**](docs/providers.md)              — คู่มือการตั้งค่าผู้ให้บริการ AI ทั้ง 9 ค่าย
- [**Languages**](docs/languages.md)              — ภาษาที่รองรับ
- [**Architecture**](docs/architecture.md)        — หลักการทำงานภายในของ hooks
- [**Troubleshooting**](docs/troubleshooting.md)  — ปัญหาที่พบบ่อยและวิธีแก้ไข

---

## ⚠️ Limitations

- **ประสบการณ์ใช้งานสตรีมมิ่งใน ท่าที่ 2**: Claude จะสตรีมภาษาอังกฤษออกมาก่อน แล้วคำแปลภาษาไทยจะปรากฏที่ด้านล่าง
- **การเรียก Ollama ครั้งแรก**: อาจใช้เวลาประมาณ 5-10 วินาที ในระหว่างที่โหลดโมเดลเข้า RAM
- **ไม่มีระบบสลับ AI เมื่อ Token หมด**: หากโควต้าของผู้ให้บริการคลาวด์หมด คุณจะได้รับข้อความแจ้งเตือน โดยระบบจะไม่สลับไปค่ายอื่นให้อัตโนมัติ
- **การตั้งค่าระดับโปรเจกต์**: ต้องนำโค้ดไปตั้งค่าเองแบบ manual (มีโค้ดแนะนำให้ตอนตั้งค่า)

---

## 🤝 Contributing

ยินดีต้อนรับนักพัฒนาทุกท่าน — ดูรายละเอียดได้ที่ [CONTRIBUTING.md](CONTRIBUTING.md) สิ่งที่พัฒนาต่อๆไปได้:
- เพิ่มการรองรับภาษาใหม่ๆ
- เพิ่มผู้ให้บริการแปลภาษาค่ายอื่น
- พัฒนาระบบ Format preservation ให้ดียิ่งขึ้น
- การเขียนเทสต์และแปลเอกสารคู่มือ

---

## 📜 License

MIT © 2026 ผู้ร่วมพัฒนา hookglot

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) สำหรับ Claude Code และระบบ hooks
- [Ollama](https://ollama.com) สำหรับ Local LLM ที่เข้าถึงง่าย
- [DeepSeek](https://platform.deepseek.com) สำหรับโมเดลภาษาที่ทำงานได้หลากหลายภาษาอย่างยอดเยี่ยม