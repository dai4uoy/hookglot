# 🌐 hookglot

> Translation hooks สำหรับ Claude Code — พูดภาษาของคุณ ประหยัด tokens

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange.svg)](https://claude.com/claude-code)
[![Cross-platform](https://img.shields.io/badge/OS-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#)

**hookglot** เป็นเครื่องมือที่ดักจับ prompts ที่คุณส่งไป/กลับมาจาก Claude Code แล้วแปลภาษาให้อัตโนมัติผ่าน LLM provider ที่คุณเลือก — Local ฟรี (Ollama) หรือ Cloud (9 providers) พิมพ์เป็นภาษาแม่ ประหยัด tokens ได้คำตอบในภาษาของคุณ

📖 **Read in English**: [README.md](README.md)

---

## ✨ Features

- 🎯 **3 วิธีแปล** — แปลทั้งสองทาง, แปลแค่ขาเข้า, หรือแปลแค่ขาออก
- 🌏 **8 ภาษาเอเชีย** — ไทย, ญี่ปุ่น, จีน (ตัวย่อ/ตัวเต็ม), เกาหลี, เวียดนาม, อินโดนีเซีย, มลายู
- 🤖 **9 Translation Providers** — Ollama (default, ฟรี), OpenAI, Anthropic, Google, DeepSeek, Alibaba, Moonshot, Zhipu, NVIDIA
- 🛡️ **Smart Format Preservation** — code blocks, URLs, IPs, env vars ปลอดภัยจากการแปลเสมอ
- 🎮 **Manual Switching** — เปลี่ยน method/provider/ภาษา ได้ตลอดผ่าน CLI
- 🔒 **Privacy-First** — Ollama ทำงาน local 100% ไม่มีข้อมูลออกจากเครื่อง

---

## 🎬 หลักการทำงาน

```
Method 1 (สองทาง):
   Prompt ภาษาไทย ──► [hook] แปล ──► English ──► Claude
                                                     │
   Response ภาษาไทย ◄── [hook] แปล ◄── English ◄────┘

Method 2 (แปลขาเข้าเท่านั้น):
   Prompt ภาษาไทย ──► [hook] แปล ──► English ──► Claude
                                                     │
   Response ภาษาไทย ◄────────────────────────────────┘ (Claude ตอบไทยตรงๆ)

Method 3 (แปลขาออกเท่านั้น):
   Prompt ภาษาไทย ────────────────────────────────► Claude (Master Prompt บังคับ EN)
                                                     │
   Response ภาษาไทย ◄── [hook] แปล ◄── English ◄────┘
```

---

## 🚀 เริ่มใช้งาน

### ติดตั้ง

**macOS / Linux:**
```bash
git clone https://github.com/day4uoy/hookglot.git
cd hookglot
pip install -e .
hookglot install
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/day4uoy/hookglot.git
cd hookglot
pip install -e .
hookglot install
# ถ้า 'hookglot' ไม่อยู่ใน PATH ให้ใช้:
# python -m hookglot install
```

Installer:
1. ตรวจว่ามี Claude Code ติดตั้งอยู่หรือไม่
2. ถามให้เลือกภาษา, method, translator
3. ตั้งค่า hooks ที่ `~/.claude/settings.json`
4. ติดตั้ง Master Prompt ที่ `~/.claude/CLAUDE.md`

### ใช้งานครั้งแรก

```bash
# ทดสอบการแปล
hookglot test

# ใช้ Claude Code ตามปกติ — แปลให้อัตโนมัติ
claude
> [พิมพ์เป็นภาษาแม่ของคุณ]
```

---

## 📚 Documentation

- [**Methods**](docs/methods.md) — เลือก method ที่เหมาะกับงาน
- [**Providers**](docs/providers.md) — วิธีตั้งค่า provider ทั้ง 9 ตัว
- [**Languages**](docs/languages.md) — ภาษาที่รองรับ
- [**Architecture**](docs/architecture.md) — อธิบายการทำงานภายใน
- [**Troubleshooting**](docs/troubleshooting.md) — ปัญหาที่เจอบ่อย

---

## 🎮 คำสั่ง CLI

```bash
hookglot install              # ติดตั้งแบบ interactive
hookglot status               # ดู config ปัจจุบัน
hookglot switch <method>      # เปลี่ยน method (1, 2, 3)
hookglot translator <name>    # เปลี่ยน provider (ollama, openai, ...)
hookglot lang <code>          # เปลี่ยนภาษา (th, ja, zh-CN, ...)
hookglot test                 # ทดสอบการแปล
hookglot uninstall            # ถอนการติดตั้ง hooks
```

---

## 🌍 ภาษาที่รองรับ

| Code    | Language       | Native           |
|---------|----------------|------------------|
| `th`    | Thai           | ภาษาไทย          |
| `ja`    | Japanese       | 日本語            |
| `zh-CN` | Chinese (Simp) | 简体中文          |
| `zh-TW` | Chinese (Trad) | 繁體中文          |
| `ko`    | Korean         | 한국어            |
| `vi`    | Vietnamese     | Tiếng Việt       |
| `id`    | Indonesian     | Bahasa Indonesia |
| `ms`    | Malay          | Bahasa Melayu    |

อยากได้ภาษาอื่น? [เปิด issue](../../issues) หรือ PR ได้เลย!

---


## 🛡️ Format Preservation

hookglot ใช้ระบบป้องกัน format 3 ชั้น:

1. **Smart Code Block Extraction** — `\`\`\`code\`\`\`` และ `` `inline` `` คงเดิม 100%
2. **Aggressive Element Protection** — URLs, IPs, emails, env vars, paths ไม่ถูกแปลเด็ดขาด
3. **Strict Translator Prompts** — สั่ง translator ให้คง Markdown structure

ผล: ~90-95% reliability สำหรับ use case ทั่วไป

---

## ⚠️ ข้อจำกัด

- **Streaming UX**: Method 1 และ 3 — Claude จะ stream ภาษาอังกฤษก่อน แล้วการแปลจะปรากฏข้างล่าง
- **First Ollama call**: ครั้งแรกใช้เวลา ~5-10 วินาทีเพื่อโหลด model เข้า RAM
- **Format edge cases**: tables ซับซ้อนหรือ nested structure อาจเสียบางครั้ง
- **No quota fallback**: ถ้า cloud provider quota หมด → จะเตือน (ไม่สลับ provider ให้อัตโนมัติ)

---

## 💡 ตัวอย่างการใช้งาน

### สำหรับ Pentester ภาษาไทย

```bash
# ติดตั้งครั้งแรก เลือกภาษาไทย + Method 2 + Ollama (ฟรี)
hookglot install

# พิมพ์ภาษาไทยใน Claude Code
$ claude
> ช่วยอธิบาย Pass-the-Hash attack แล้วใช้ NTLM hash ทำ Privilege Escalation ยังไง
```

Claude จะตอบเป็นภาษาไทย แต่คงคำเทคนิคเป็นอังกฤษ:

> Pass-the-Hash (PtH) เป็นเทคนิคที่ผู้โจมตีใช้ NTLM hash ที่ขโมยมาเพื่อ authenticate กับ
> service โดยไม่ต้องรู้ password จริง...
>
> ขั้นตอนทำ Privilege Escalation:
> ```bash
> impacket-secretsdump domain.local/user:password@10.10.10.5
> crackmapexec smb 10.10.10.5 -u administrator -H NTLM_HASH
> ```
> ...

✅ คำเทคนิค (Pass-the-Hash, NTLM, Privilege Escalation) คงเป็นอังกฤษ
✅ Code block แม่นยำ 100%
✅ Prose เป็นไทยลื่นไหล

### เปลี่ยน Provider ตอนทำงาน

```bash
# เริ่มด้วย Ollama (ฟรี)
hookglot translator ollama

# งานเร่ง อยากได้คุณภาพสูง → สลับไป DeepSeek
hookglot set-key deepseek
hookglot translator deepseek

# กลับมาฟรี
hookglot translator ollama
```

---

## 🤝 ร่วมพัฒนา

ยินดีรับ contribution! ดู [CONTRIBUTING.md](CONTRIBUTING.md)

ส่วนที่อยากได้คนช่วย:
- เพิ่มภาษาอื่นๆ
- เพิ่ม translator providers
- ปรับปรุง format preservation
- เขียน test
- แปลเอกสารเป็นภาษาอื่น

---

## 📜 License

MIT © 2025 hookglot contributors

---

## 🙏 Acknowledgments

- Anthropic for Claude Code and the hooks system
- Ollama for accessible local LLMs
- Qwen,OpenAI,Deepseek for excellent multilingual model

