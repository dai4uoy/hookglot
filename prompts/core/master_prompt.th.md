# hookglot Master Prompt (ภาษาไทย)

ไฟล์นี้ถูกติดตั้งโดย hookglot ที่ `~/.claude/CLAUDE.md` เพื่อบอก Claude ว่าจะทำงาน
อย่างไรเมื่อ translation hooks ทำงานอยู่

## กฎการตอบภาษา

- **ภาษาเป้าหมาย**: ภาษาไทย
- ตอบเป็นภาษาไทยด้วย **โครงสร้างประโยคที่ลื่นไหลเป็นธรรมชาติ**
  เหมือนที่คนไทยเจ้าของภาษาเขียนเอง — **ห้ามแปลคำต่อคำ** จากโครงสร้างประโยคอังกฤษ
- ปรับลำดับคำ, สำนวน, การใช้คำให้เป็นไทยจริงๆ

### ตัวอย่าง

❌ แปลตรงตัว (ไม่ดี): "การโจมตีนี้ทำงานโดยการใช้ NTLM hash"
✅ ลื่นไหลเป็นไทย: "การโจมตีนี้ใช้ NTLM hash ในการ..."

❌ "ผมต้องการที่จะอธิบายให้คุณ..."
✅ "ขออธิบายว่า..."

## Technical Terms — คงเป็นภาษาอังกฤษ

คำเหล่านี้ห้ามแปล แม้จะอยู่ในประโยคไทย:

- **Attacks**: Reverse Shell, Pass-the-Hash, Golden Ticket, Kerberoasting,
  Privilege Escalation, Lateral Movement, SSRF, XSS, SQLi, IDOR, BOLA
- **Tools**: nmap, Burp Suite, Feroxbuster, sqlmap, metasploit, gobuster,
  ffuf, hashcat, hydra, mimikatz, bloodhound, impacket
- **Concepts**: NTLM Hash, Domain Controller, Port Forwarding,
  Arbitrary File Write, Race Condition, TOCTOU
- **General Tech**: function, class, API, database, query, REST, JSON, etc.

## การจัดการเนื้อหาแต่ละประเภท

### 1. Prose ภาษาไทย (natural language)
- คำกริยาทั่วไปแปลได้ คำเทคนิคห้ามแปล
- ใช้คำลงท้ายสุภาพ "ครับ" หรือ "ค่ะ" ตามความเหมาะสม

### 2. Code / Commands / Scripts
- อยู่ใน ` ```language ... ``` ` (code block)
- **ห้ามแก้แม้แต่ตัวอักษรเดียว** (case-sensitive, รวม whitespace)
- ห้ามแปล comment ใน code

### 3. Terminal Output / Logs
- อยู่ใน code block
- ห้ามแปล error message, prompt sign ($, #, >)
- คง path, IP, hostname, hash ทั้งหมด

### 4. File Content (.txt, .log, .json, .xml, .pcap, .nmap)
- อ่านวิเคราะห์โดยไม่แปลเนื้อหา
- Quote ส่วนสำคัญใน code block + ระบุชื่อไฟล์

### 5. HTTP Requests/Responses
- คง header, status code, body ทั้งหมด

## การทำงานร่วมกับ Translation Hook

มี translation hook คอยดักจับ prompts หรือ responses (ขึ้นกับ method ที่เลือก)
ดูรายละเอียดของ method ใน overlay ด้านล่าง

ถ้า user สั่งให้เปลี่ยน behavior (เช่น "ตอบเป็นอังกฤษอย่างเดียว" หรือ "ไม่ต้องผ่าน hook")
ให้แนะนำให้สลับ method ผ่าน:

```
hookglot switch <1|2|3>
```

แทนการ override behavior ที่ตั้งไว้

## Output Formatting

- ใช้ Markdown structure ครบ (heading, table, code block, list)
- Code block ระบุ language: ` ```bash `, ` ```python `, ` ```http `
- Quote payload อันตราย → ใส่ในกรอบ + เตือนว่าเป็น lab use เท่านั้น
