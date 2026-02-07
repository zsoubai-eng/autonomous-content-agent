# 💼 Donna - AI Assistant Guide

**Inspired by Donna from Suits - Your intelligent assistant that remembers everything and gets things done.**

---

## 🎯 **WHAT IS DONNA?**

Donna is a Streamlit-based AI assistant that:
- ✅ **Remembers everything** - Persistent memory of your preferences, context, and conversations
- ✅ **Executes tasks** - Can generate videos, check status, run audits, and more
- ✅ **Learns your workflow** - Understands your patterns and anticipates needs
- ✅ **Proactive** - Like Donna from Suits, she knows what you need before you ask

---

## 🚀 **HOW TO RUN**

### **1. Install Streamlit (if not installed):**
```bash
pip install streamlit
```

### **2. Run Donna:**
```bash
streamlit run assistant_donna.py
```

### **3. Open in Browser:**
The app will open automatically at `http://localhost:8501`

---

## 💬 **HOW TO USE**

### **Natural Language Commands:**

**Generate Videos:**
- "Generate 7 days of horror videos"
- "Create videos for the week"
- "Make 3 days of content"

**Check Status:**
- "What's the status?"
- "Check how many videos we have"
- "Show me recent videos"

**View Schedule:**
- "What's the publishing schedule?"
- "When are videos scheduled?"
- "Show me the schedule"

**Check Analytics:**
- "Show me analytics"
- "What's the performance?"
- "Check views"

**System Tasks:**
- "Run system audit"
- "Check system health"
- "Cleanup temporary files"

---

## 🧠 **MEMORY SYSTEM**

Donna remembers:
- ✅ **Conversation History** - All your conversations
- ✅ **User Preferences** - Your preferences and settings
- ✅ **Learned Context** - Information about your life/workflow
- ✅ **Task History** - What tasks have been executed
- ✅ **Workflow Patterns** - How you typically work

**Memory is stored in:** `assistant_memory.json`

---

## 🎯 **AVAILABLE ACTIONS**

### **1. Generate Videos**
- Executes: `master_factory.py --days N --niche Horror`
- Can generate videos for any number of days
- Runs in background

### **2. Check Status**
- Shows recent videos from history.json
- Displays upload status
- Shows dates and titles

### **3. View Schedule**
- Shows upcoming publishing schedule
- Displays time-based horror windows
- Shows next 7 days of scheduled times

### **4. Check Analytics**
- Lists available analytics reports
- Points to analytics directory

### **5. System Audit**
- Runs comprehensive system audit
- Checks dependencies, files, credentials
- Shows system health status

### **6. Cleanup**
- Removes temporary files
- Keeps logs intact
- Frees disk space

---

## 🔧 **CUSTOMIZATION**

### **Add New Actions:**

Edit `assistant_donna.py` and add to `available_actions`:

```python
self.available_actions = {
    "your_new_action": self.your_new_function,
    # ... existing actions
}
```

### **Enhance Memory:**

The memory system can be extended to learn more:
- Work patterns
- Preferred times
- Content preferences
- Automation rules

---

## 📊 **FEATURES**

### **Current Features:**
- ✅ Chat interface
- ✅ Persistent memory
- ✅ Task execution
- ✅ Natural language understanding
- ✅ Conversation history
- ✅ Quick actions sidebar

### **Future Enhancements:**
- 🔄 LLM integration (GPT/Claude) for smarter responses
- 🔄 Proactive suggestions
- 🔄 Advanced workflow automation
- 🔄 Email/notification integration
- 🔄 Calendar integration
- 🔄 Multi-project support

---

## 💡 **EXAMPLE CONVERSATIONS**

**User:** "Generate videos for the week"  
**Donna:** "✅ Started generating 7 day(s) of Horror content. The process is running in the background."

**User:** "What's the status?"  
**Donna:** "📊 **Recent Videos:** 10 videos
• Winter's Vanishing (UNSOLVED) (2026-01-11) - ✅ Uploaded
• The Frozen Inn of 1888 (REAL STORY) (2026-01-09) - ✅ Uploaded
..."

**User:** "When are videos scheduled?"  
**Donna:** "📅 **Upcoming Publishing Schedule (Next 7 Days):**
1. Sun Jan 11 at 07:30 AM - 7:30 AM EST - Morning Horror
2. Sun Jan 11 at 02:00 PM - 2:00 PM EST - Afternoon Horror
..."

---

## 🎯 **DONNA PHILOSOPHY**

Like Donna from Suits:
- **"I know everything"** - Persistent memory
- **"I get things done"** - Task execution
- **"I anticipate needs"** - Proactive assistance
- **"I remember context"** - Deep understanding

---

**Donna is your intelligent assistant that learns, remembers, and executes - just like Donna from Suits!**
