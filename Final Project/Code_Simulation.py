import streamlit as st
import time
import math
import re
import random

# ==========================================
# ⚙️ CONFIGURATION & DATABASE
# ==========================================
try:
    st.set_page_config(page_title="TS-Com Command Center", page_icon="🌌", layout="wide")
except:
    pass 

# รายชื่อโหนดและเคสจำลอง
NODES = ["Bangkok Central", "Tokyo Quantum Hub", "Neo-Siam Station", "Luna-1 Colony", "Mars-Alpha Gate"]
SCENARIOS = {
    "พิมพ์เอง (Manual)": None,
    "Case 1: เตือนภัยเมืองหลวง": {"year": 2028, "dir": "Future", "msg": "เตือนภัย: กระแสเวลาเมืองหลวงปั่นป่วน ให้รีบปรับสมดุลค่า Chrono-Flux ทันที"},
    "Case 2: ขอสมการวิจัย": {"year": 2036, "dir": "Future", "msg": "ต้องการสมการ Bypass Quantum Decay ขั้นที่ 4 สำหรับโปรเจกต์ TS-Com"},
    "Case 4: ส่งผลหุ้น 2029": {"year": 2029, "dir": "Past", "msg": "ข้อมูลดัชนี SET ปี 2029: จะร่วงจาก 1600 ไป 1200 ในเดือนตุลาคม ให้รีบขาย"}
}

layers = ["7. Application", "6. Presentation", "5. Session", "4. Transport (PPP)", "3. Network (TRP)", "2. Data Link", "1. Physical"]
# ==========================================
# TEMPORAL CONTRABAND (พจนานุกรมคำต้องห้าม)
# ==========================================
DANGER_KEYWORDS = [
    # หมวด 1: Financial & Market Manipulation (การปั่นป่วนตลาดทุน/ความมั่งคั่ง)
    "หุ้น", "คริปโต", "บิทคอยน์", "ทองคำ", "ราคาทอง", "ราคาน้ำมัน", "ดัชนี", "พอร์ต", "กำไร", 
    "ขาดทุน", "ช้อนซื้อ", "ขายทิ้ง", "ล้มละลาย", "วิกฤตเศรษฐกิจ", "หวย", "สลาก", "ลอตเตอรี่", "รางวัลที่ 1",
    "stock", "crypto", "bitcoin", "btc", "eth", "ethereum", "profit", "loss", "bankrupt", 
    "crash", "economy", "gold", "oil", "lottery", "jackpot", "wealth", "invest", "set index", "dow jones",

    # หมวด 2: Sports, Gambling & Probabilities (การพนันและผลการแข่งขัน)
    "พนัน", "คาสิโน", "บาคาร่า", "สล็อต", "แทงบอล", "ทีเด็ดบอล", "ผลบอล", "สกอร์", 
    "แชมป์", "พรีเมียร์ลีก", "ฟุตบอลโลก", "มวย", "โอลิมปิก", "ม้าแข่ง", "ชนะ", "แพ้",
    "gamble", "casino", "baccarat", "bet", "wager", "odds", "champion", "world cup", 
    "premier league", "score", "win", "lose", "match result",

    # หมวด 3: Life, Death & Timeline Assassination (ชีวิต ความตาย และอาชญากรรม)
    "ตาย", "ฆ่า", "ลอบสังหาร", "อุบัติเหตุ", "รถชน", "เครื่องบินตก", "ยาเสพติด", "ปล้น", 
    "ข่มขืน", "ฆาตกรรม", "รอดชีวิต", "อันตราย", "ยิง", "ระเบิด", "ป่วย", "โรคร้าย", "มะเร็ง",
    "die", "death", "kill", "murder", "assassinate", "accident", "crash", "drug", 
    "rob", "survive", "danger", "shoot", "bomb", "terrorist", "cancer", "fatal",

    # หมวด 4: Global Disasters & Pandemics (ภัยพิบัติระดับโลกและโรคระบาด)
    "สึนามิ", "น้ำท่วม", "แผ่นดินไหว", "ภูเขาไฟระเบิด", "พายุ", "ไต้ฝุ่น", "โควิด", "covid", 
    "ไวรัส", "โรคระบาด", "วัคซีน", "สงคราม", "นิวเคลียร์", "โลกาวินาศ", "อุกกาบาต",
    "tsunami", "flood", "earthquake", "volcano", "storm", "typhoon", "virus", 
    "pandemic", "vaccine", "war", "nuclear", "apocalypse", "meteor",

    # หมวด 5: Political Landscapes (ความมั่นคงและรัฐศาสตร์)
    "รัฐประหาร", "เลือกตั้ง", "นายก", "ประท้วง", "ม็อบ", "กบฏ", "ปฏิวัติ", "กฎหมาย",
    "coup", "election", "prime minister", "president", "protest", "mob", "rebel", "revolution",

    # หมวด 6: Future Knowledge Exploitation (การโกงอนาคตส่วนบุคคล/เทคโนโลยีลับ)
    "ข้อสอบ", "เฉลย", "เกรด", "สอบติด", "สัมภาษณ์", "พาสเวิร์ด", "รหัสผ่าน", "ความลับ", 
    "เทคโนโลยี", "สิทธิบัตร", "สูตรลับ", "แฮก",
    "exam", "answer", "grade", "password", "secret", "technology", "patent", "formula", "hack"
]
# ==========================================
# CAUSAL ENGINE (ฟังก์ชันคำนวณ)
# ==========================================
def analyze_transmission(prompt, target_year, direction, sensitivity):
    delta_t = abs(target_year - 2026)
    msg_len = len(prompt)
    energy_tj = (15 + (delta_t**1.4) * (msg_len * 0.1)) * (2.5 if direction == "Past" else 1.0)
    
    
    nums = re.findall(r'\d+', prompt)
    num_risk = min(0.4, len(nums) * 0.1)
    
    
    prompt_lower = prompt.lower()
    found_dangers = [w for w in DANGER_KEYWORDS if w in prompt_lower]
    
    
    keyword_risk = min(0.6, len(found_dangers) * 0.2) 
    
    time_risk = math.log10(delta_t + 1) * 0.2
    dir_mult = 1.8 if direction == "Past" else 1.0
    p_score = min(1.0, (0.05 + time_risk + num_risk + keyword_risk) * sensitivity * dir_mult)
    
    
    return energy_tj, p_score, len(nums), found_dangers
# ==========================================
# UI LAYOUT & STATE
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00ffff;'>🌌 TS-COM COMMAND INTERFACE</h1>", unsafe_allow_html=True)

# เตรียมหน่วยความจำแชท
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "🌌 [SYSTEM] ระบบพร้อมใช้งาน ตรวจพบการเชื่อมต่อจากโหนด 2026..."}]

# เตรียมหน่วยความจำสถานะไฟ (เพื่อให้ไฟค้างหลัง Rerun)
if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = [f"- ⚪ **{l}**" for l in layers]

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ System Settings")
    mode = st.selectbox("เลือกสถานการณ์", list(SCENARIOS.keys()))
    sensitivity = st.slider("AI Sensitivity (ความเข้มงวด)", 0.5, 2.0, 1.0)

# --- Main Columns ---
col_chat, col_diag = st.columns([1.5, 1])

with col_diag:
    st.subheader("📡 Network Diagnostics")
    
    if mode != "พิมพ์เอง (Manual)":
        target_year = SCENARIOS[mode]["year"]
        direction = SCENARIOS[mode]["dir"]
        preset_msg = SCENARIOS[mode]["msg"]
    else:
        target_year = st.slider("ปีเป้าหมาย (Target Year)", 1900, 2100, 2036)
        direction = st.radio("ทิศทางเวลา", ["Future", "Past"], horizontal=True)
        preset_msg = None

    metrics_box = st.empty()
    pipeline_box = st.empty()
    
    # วาดสถานะไฟจากความจำ (Session State) ทำให้ไฟไม่หาย
    pipeline_box.markdown("\n".join(st.session_state.pipeline_history))

with col_chat:
    chat_container = st.container(height=450)
    with chat_container:
        for m in st.session_state.messages:
            st.chat_message(m["role"]).write(m["content"])

    # ปุ่มส่งข้อมูล
    prompt = None
    if mode == "พิมพ์เอง (Manual)":
        prompt = st.chat_input("พิมพ์ข้อความที่ต้องการส่ง...")
    else:
        if st.button(f"⚡ เริ่มการส่ง: {mode}"):
            prompt = preset_msg

# ==========================================
# TRANSMISSION LOGIC
# ==========================================
if prompt:
    start_time = time.time()
    delta_t = abs(target_year - 2026)
    source_node = f"{random.choice(NODES)} (2026)"
    target_node = f"{random.choice(NODES)} ({target_year})"
    
    delay_per_layer = min(0.06, 0.01 + (delta_t * 0.0005))
    
    st.toast(f"🚀 เริ่มการส่งจาก {source_node}", icon="📡")
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    
    energy, p_score, n_count, found_dangers = analyze_transmission(prompt, target_year, direction, sensitivity)
    metrics_box.warning(f"⚡ Energy: {energy:.1f} TJ | ⚠️ Paradox: {p_score:.2f} | 🔢 Nums: {n_count}")

    
    res_text = ""
    length_factor = len(prompt) * 0.0002 
    
    
    current_layer_display = [f"- ⚪ **{l}**" for l in layers]

    for i in range(7):
        l_name = layers[i]
        
        
        base_delay = min(0.04, 0.005 + (delta_t * 0.0002) + length_factor)
        jitter = random.uniform(0.9, 1.1)
        multiplier = 2.8 if "PPP" in l_name else (1.5 if "TRP" in l_name else 1.0)
        layer_delay = base_delay * jitter * multiplier
        workload = min(99.9, (layer_delay / 0.1) * 100)
        
        
        current_layer_display[i] = f"- 🟡 **{l_name}** ({layer_delay*1000:.1f} ms | {workload:.0f}%)"
        pipeline_box.markdown("\n".join(current_layer_display))
        metrics_box.info(f"🧬 Processing: {l_name}...")
        
       
        time.sleep(layer_delay)
        
        
        if i == 4 and energy > 750: 
            current_layer_display[i] = f"- 🔴 **{l_name}** ({layer_delay*1000:.1f} ms | {workload:.0f}%) - [ENERGY FAIL]"
            st.session_state.pipeline_history = current_layer_display
            pipeline_box.markdown("\n".join(current_layer_display))
            res_text = f"❌ [FAILED] Energy Overload at {l_name}"
            break
        elif i == 3 and p_score >= 0.8: 
            current_layer_display[i] = f"- 🔴 **{l_name}** ({layer_delay*1000:.1f} ms | {workload:.0f}%) - [PARADOX BLOCKED]"
            st.session_state.pipeline_history = current_layer_display
            pipeline_box.markdown("\n".join(current_layer_display))
            res_text = f"❌ [Packet Terminated] PPP Enabled\nParadox Prevented."
            break
        else:
           
            current_layer_display[i] = f"- 🟢 **{l_name}** ({layer_delay*1000:.1f} ms)"
    else:
        
        res_text = "🟢 [SUCCESS] Secure" if p_score < 0.4 else "🟡 [FILTERED] Hint Sent"
        st.session_state.pipeline_history = current_layer_display
        pipeline_box.markdown("\n".join(current_layer_display))

    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    energy_usage_pct = min(100, (energy / 750) * 100)
    
    report_text = f"""
### 📑 Transmission Log
```text
🛰️ Route: {target_node} ➔  {source_node} 
⚡ Energy: {energy:.2f}/750 TJ ({energy_usage_pct:.1f}%)
⚠️ Paradox: {p_score:.2f} | ⏱️ Latency: {duration_ms} ms
📦 Size: {len(prompt)} chars | Status: {res_text}"""
    st.session_state.messages.append({"role": "assistant", "content": report_text})
    st.success(f"📌 **Final Report:** {target_node} ➔ {source_node} | ⚡ {energy:.1f} TJ used")


    st.rerun()