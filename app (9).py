import streamlit as st
import sqlite3
from datetime import datetime
from urllib.parse import quote_plus

st.set_page_config(page_title="JAMBLOOM", page_icon="🌸", layout="wide")
DB = "jambloom_history.db"

# Fixed light palette: independent of the user's operating-system theme.
st.markdown("""
<style>
:root { color-scheme: light !important; }
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stSidebar"] {
  color-scheme: light !important; background:#F7F5EF !important; color:#263A32 !important;
}
[data-testid="stSidebar"] { background:#E9EEE8 !important; }
.block-container {max-width:1180px;padding-top:1.7rem;padding-bottom:3rem;}
h1,h2,h3 {color:#214B3B !important;}
p,label,li {color:#263A32;}
div[data-testid="stMetric"] {background:white;border:1px solid #DCE4DB;padding:14px;border-radius:14px;}
.stButton>button,.stFormSubmitButton>button {
 background:#285B45!important;color:white!important;border:0!important;border-radius:10px!important;font-weight:650!important;
}
.jhero {background:linear-gradient(120deg,#214B3B,#39745A);padding:2rem 2.2rem;border-radius:22px;margin-bottom:1.2rem;color:white;}
.jhero h1 {color:white!important;font-size:2.7rem;margin:0;}
.jhero p {color:#F1F5EF!important;margin:.4rem 0 0;font-size:1.08rem;}
.jcard {background:white;border:1px solid #DCE4DB;border-radius:16px;padding:1.1rem;height:100%;}
.jtag {display:inline-block;background:#E7EFE8;color:#285B45;padding:.25rem .65rem;border-radius:30px;font-size:.82rem;font-weight:700;}
.smallnote {color:#596B62!important;font-size:.9rem;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

COURSES = {
"Medicine and Surgery": (["English Language","Biology","Chemistry","Physics"], "Medicine, Surgery, Anatomy and Physiology", "Verify the exact requirements for your chosen institution."),
"Nursing Science": (["English Language","Biology","Chemistry","Physics"], "Nursing, Midwifery and Public Health", "Check the current institutional and O'Level requirements."),
"Pharmacy": (["English Language","Biology","Chemistry","Physics"], "Pharmacy and Pharmaceutical Sciences", "Chemistry and Biology are important preparation subjects."),
"Medical Laboratory Science": (["English Language","Biology","Chemistry","Physics"], "Biomedical and Medical Laboratory Science", "Confirm the current requirements with each institution."),
"Computer Science": (["English Language","Mathematics","Physics","One other accepted science subject"], "Computer Science, Software Engineering and IT", "The fourth subject can vary; verify it on JAMB IBASS."),
"Software Engineering": (["English Language","Mathematics","Physics","One other accepted subject"], "Software Engineering and Computing", "Confirm the accepted fourth subject with your preferred institution."),
"Civil Engineering": (["English Language","Mathematics","Physics","Chemistry"], "Civil and Structural Engineering", "Mathematics, Physics and Chemistry are central to this pathway."),
"Electrical/Electronics Engineering": (["English Language","Mathematics","Physics","Chemistry"], "Electrical and Electronics Engineering", "Confirm the current programme requirements."),
"Accounting": (["English Language","Mathematics","Economics","One other accepted subject"], "Accounting, Finance and Banking", "Accepted fourth subjects differ across institutions."),
"Economics": (["English Language","Mathematics","Economics","One other accepted subject"], "Economics and Development Studies", "Check the subject list for your chosen institution."),
"Law": (["English Language","Literature in English","One Arts subject","One other accepted Arts/Social Science subject"], "Law and Legal Studies", "Accepted Arts and Social Science subjects may vary."),
"Mass Communication": (["English Language","Literature in English","One Arts subject","One Social Science subject"], "Journalism, Public Relations and Mass Communication", "Verify the exact combination for your institution."),
"Political Science": (["English Language","Government","One Arts/Social Science subject","One other accepted subject"], "Political Science and International Relations", "Institutional requirements can differ."),
"Architecture": (["English Language","Mathematics","Physics","One accepted subject such as Chemistry, Geography or Fine Arts"], "Architecture and Building Technology", "Check whether your preferred school specifies a particular fourth subject."),
"Agriculture": (["English Language","Chemistry","Biology or Agriculture","One other accepted science subject"], "Agriculture and Agricultural Economics", "Accepted combinations vary by programme."),
"Education": (["English Language","Two subjects related to your teaching specialisation","One other accepted subject"], "Education and subject-specific teaching programmes", "Your subjects depend on the teaching specialisation.")
}

# Original challenging practice questions, five per subject.
Q = [
("Use of English","Hardly had the committee reached a decision _____ the chairman requested a recount.",["when","than","then","while"],"when","The standard correlative construction is 'hardly...when'."),
("Use of English","Choose the word nearest in meaning to 'mitigate' in: The policy may mitigate the effects of inflation.",["intensify","reduce","predict","conceal"],"reduce","Mitigate means to make something less severe or harmful."),
("Use of English","Which sentence is grammatically correct?",["Neither the principal nor the teachers was present.","Neither the principal nor the teachers were present.","Neither the teachers nor the principal were present.","Neither the principal or the teachers were present."],"Neither the principal nor the teachers were present.","With neither...nor, the verb generally agrees with the nearer subject, 'teachers'."),
("Use of English","In 'The proposal, together with its supporting documents, was submitted', the phrase between commas:",["is the grammatical subject","does not change the number of the subject","makes the subject compound","is the direct object"],"does not change the number of the subject","The subject is 'The proposal'; the intervening phrase does not make it plural."),
("Use of English","'If I had known about the change, I would have attended' implies that the speaker:",["attended after learning of it","did not know and did not attend","knew but chose not to attend","will attend a future event"],"did not know and did not attend","This is a past unreal conditional describing an event that did not happen."),
("Mathematics","If 3^(x+1) = 81, find x.",["2","3","4","5"],"3","81 = 3^4, so x + 1 = 4 and x = 3."),
("Mathematics","The roots of 2x² − 7x + 3 = 0 are p and q. Find p² + q².",["31/4","37/4","43/4","49/4"],"37/4","p+q=7/2 and pq=3/2; p²+q²=(p+q)²−2pq=37/4."),
("Mathematics","A bag has 5 red, 4 blue and 3 green balls. Two are drawn without replacement. Find the probability both are blue.",["1/11","1/9","1/6","2/11"],"1/11","(4/12) × (3/11) = 1/11."),
("Mathematics","An arithmetic progression has first term 7 and common difference 4. Which term is 55?",["11th","12th","13th","14th"],"13th","7 + (n−1)4 = 55, so n = 13."),
("Mathematics","A sector has radius 7 cm and angle 120°. Using π=22/7, find its arc length.",["22/3 cm","44/3 cm","22 cm","28 cm"],"44/3 cm","Arc length = (120/360) × 2πr = 44/3 cm."),
("Biology","A plant cell is placed in a solution more concentrated than its cell sap. What happens to water initially?",["Water enters by active transport.","Water leaves by osmosis.","Solutes leave and water remains constant.","Water and solutes enter equally."],"Water leaves by osmosis.","The external solution has lower water potential, so water moves out through the selectively permeable membrane."),
("Biology","In a Tt × Tt cross, where T is dominant for tallness, what proportion of offspring is expected to be short?",["0","1/4","1/2","3/4"],"1/4","The possible genotypes are TT, Tt, Tt and tt; only tt is short."),
("Biology","Which event directly causes sister chromatids to separate during mitosis?",["The nuclear membrane reforms.","Centromeres divide and spindle fibres pull chromatids apart.","DNA replicates again.","Homologous chromosomes pair."],"Centromeres divide and spindle fibres pull chromatids apart.","During anaphase, sister chromatids separate and move to opposite poles."),
("Biology","In grass → grasshopper → frog → snake, what may happen immediately if the frog population falls sharply?",["Grasshopper numbers may increase.","Grasshopper numbers must fall to zero.","Grass production immediately stops.","Snake numbers must increase."],"Grasshopper numbers may increase.","Reduced predation by frogs may allow grasshopper numbers to rise."),
("Biology","Why do arteries generally have thicker muscular walls than veins?",["They carry blood at higher pressure.","They contain valves at regular intervals.","They carry only deoxygenated blood.","They always carry oxygenated blood."],"They carry blood at higher pressure.","Their thick, elastic and muscular walls withstand the higher pressure of blood leaving the heart."),
("Chemistry","What volume of 0.20 mol/dm³ NaOH contains 0.005 mol of NaOH?",["10 cm³","20 cm³","25 cm³","40 cm³"],"25 cm³","V=n/C=0.005/0.20=0.025 dm³=25 cm³."),
("Chemistry","Which pair is most likely to form a buffer solution?",["HCl and NaCl","CH₃COOH and CH₃COONa","NaOH and KCl","HNO₃ and NaNO₃"],"CH₃COOH and CH₃COONa","A weak acid and its conjugate base form an acidic buffer."),
("Chemistry","An element has electron arrangement 2,8,7. What is its likely compound formula with magnesium (2,8,2)?",["MgCl","MgCl₂","Mg₂Cl","Mg₂Cl₃"],"MgCl₂","Magnesium forms Mg²⁺ and chlorine forms Cl⁻, giving MgCl₂."),
("Chemistry","Which change increases the rate of reaction between a solid and aqueous acid?",["Using larger solid pieces","Reducing the temperature","Increasing exposed surface area","Diluting the acid"],"Increasing exposed surface area","More exposed surface allows more frequent effective collisions."),
("Chemistry","What is the oxidation number of sulfur in H₂SO₄?",["+2","+4","+6","−2"],"+6","2(+1) + S + 4(−2) = 0, therefore sulfur is +6.")
]

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS history
        (id INTEGER PRIMARY KEY, label TEXT, score INTEGER, total INTEGER, percent REAL, taken_at TEXT)""")
        con.commit()

def save_score(label, score, total):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO history(label,score,total,percent,taken_at) VALUES(?,?,?,?,?)",
                    (label, score, total, round(score/total*100,1), datetime.now().strftime("%Y-%m-%d %H:%M")))
        con.commit()

def read_history(label):
    with sqlite3.connect(DB) as con:
        return con.execute("SELECT score,total,percent,taken_at FROM history WHERE label=? ORDER BY id DESC LIMIT 20",(label,)).fetchall()

init_db()

st.markdown("""
<div class="jhero">
 <div style="letter-spacing:.16em;font-weight:700;color:#DCEBDD;font-size:.85rem">YOUR ACADEMIC COMPASS</div>
 <h1>🌸 JAMBLOOM</h1>
 <p>Explore your options. Prepare with purpose. Let your future bloom.</p>
</div>
""", unsafe_allow_html=True)

if "quiz_complete" not in st.session_state: st.session_state.quiz_complete = False
if "answers" not in st.session_state: st.session_state.answers = {}

with st.sidebar:
    st.markdown("## 🌸 JAMBLOOM")
    st.caption("JAMB and course guidance")
    label = st.text_input("Name or nickname (optional)", value=st.session_state.get("label","My Practice"))
    st.session_state.label = label.strip() or "My Practice"
    page = st.radio("Navigate",["Home","Course Adviser","JAMB Practice","University Finder","My Progress"])
    st.divider()
    st.caption("For SS2 and SS3 students · No account or sign-in required.")

if page == "Home":
    st.subheader("Welcome to your next step.")
    st.write("JAMBLOOM brings course exploration, subject guidance and exam practice into one student-friendly space.")
    a,b,c = st.columns(3)
    a.markdown('<div class="jcard"><span class="jtag">01 · EXPLORE</span><h3>Course Adviser</h3><p>Explore courses and suggested UTME subject combinations.</p></div>',unsafe_allow_html=True)
    b.markdown('<div class="jcard"><span class="jtag">02 · PRACTISE</span><h3>JAMB Practice</h3><p>Challenge yourself with demanding questions and explanations.</p></div>',unsafe_allow_html=True)
    c.markdown('<div class="jcard"><span class="jtag">03 · PLAN</span><h3>University Finder</h3><p>Search for institutions by course and location.</p></div>',unsafe_allow_html=True)
    st.markdown("### Get started")
    st.markdown("1. Select a course in **Course Adviser**.\n2. Test your understanding in **JAMB Practice**.\n3. Explore options in **University Finder**.\n4. Review saved results in **My Progress**.")
    st.info("Always verify current subject combinations and admission requirements through official JAMB IBASS and your chosen university.")
    st.link_button("Open JAMB IBASS","https://ibass.jamb.gov.ng/")

elif page == "Course Adviser":
    st.subheader("Course Adviser")
    st.write("Choose a course to view a suggested UTME subject combination.")
    course = st.selectbox("Select a course",list(COURSES.keys()))
    subjects, related, note = COURSES[course]
    st.markdown(f"### {course}")
    st.markdown("**Suggested UTME subjects**")
    for n, subject in enumerate(subjects,1):
        st.write(f"{n}. {subject}")
    st.markdown(f"**Related study areas:** {related}")
    st.info(note)
    st.warning("These are guidance suggestions, not a replacement for checking the current JAMB IBASS requirements and your chosen university's admission page.")
    st.link_button("Verify on official JAMB IBASS","https://ibass.jamb.gov.ng/")

elif page == "JAMB Practice":
    st.subheader("JAMB Practice Challenge")
    st.write("20 challenging original questions: five each in Use of English, Mathematics, Biology and Chemistry.")
    st.caption("These are original practice questions, not official JAMB past questions.")
    if not st.session_state.quiz_complete:
        with st.form("practice_form"):
            selected = {}
            for i,(subject,question,options,answer,explanation) in enumerate(Q):
                st.markdown(f"**Question {i+1} · {subject}**")
                st.write(question)
                selected[str(i)] = st.radio("Choose an answer",options,key=f"q_{i}",index=None,label_visibility="collapsed")
                st.divider()
            submit = st.form_submit_button("Submit answers",use_container_width=True)
        if submit:
            missing = [i for i,v in selected.items() if v is None]
            if missing:
                st.error(f"Please answer all questions. You have {len(missing)} unanswered.")
            else:
                st.session_state.answers = selected
                st.session_state.quiz_complete = True
                st.rerun()
    else:
        answers = st.session_state.answers
        score = sum(answers.get(str(i)) == item[3] for i,item in enumerate(Q))
        percent = round(score/len(Q)*100)
        st.markdown("### Your result")
        x,y,z = st.columns(3)
        x.metric("Score",f"{score}/20"); y.metric("Percentage",f"{percent}%"); z.metric("Questions",20)
        if percent >= 80: st.success("Excellent performance. Keep practising to maintain this standard.")
        elif percent >= 60: st.info("Good effort. Review the explanations and strengthen the topics you missed.")
        else: st.warning("Use this result as a guide. Revise the explanations and try again.")
        breakdown = {}
        for i,item in enumerate(Q):
            breakdown.setdefault(item[0],[0,0]); breakdown[item[0]][1] += 1
            if answers[str(i)] == item[3]: breakdown[item[0]][0] += 1
        st.markdown("### Subject breakdown")
        cols = st.columns(4)
        for col,(subject,result) in zip(cols,breakdown.items()):
            col.metric(subject,f"{result[0]}/{result[1]}")
        st.markdown("### Answer review")
        for i,item in enumerate(Q):
            with st.expander(f"{'✓' if answers[str(i)] == item[3] else '✗'} Question {i+1} · {item[0]}"):
                st.write(item[1]); st.write(f"Your answer: {answers[str(i)]}")
                st.write(f"Correct answer: {item[3]}"); st.write(f"Explanation: {item[4]}")
        if st.button("Save result to My Progress"):
            save_score(st.session_state.label,score,20)
            st.success("Result saved on this device.")
        if st.button("Try again with the practice set"):
            st.session_state.quiz_complete = False
            st.session_state.answers = {}
            st.rerun()

elif page == "University Finder":
    st.subheader("University Finder")
    st.write("Search for institutions that may offer your preferred programme.")
    course = st.text_input("Course or programme",placeholder="e.g. Computer Science")
    location = st.text_input("Preferred state or location",placeholder="e.g. Lagos")
    if st.button("Search universities",use_container_width=True):
        if not course.strip() or not location.strip():
            st.error("Enter both a course and a location.")
        else:
            search_url = "https://www.google.com/search?q=" + quote_plus(f"universities in {location} offering {course} Nigeria")
            st.link_button("View university search results",search_url)
            st.caption("Search results are a starting point. Confirm accreditation, course availability and admission requirements on each institution's official website.")

else:
    st.subheader("My Progress")
    st.write("Quiz results saved on this device. No student account is needed.")
    history = read_history(st.session_state.label)
    if history:
        st.metric("Saved attempts",len(history))
        st.dataframe([{"Score":f"{r[0]}/{r[1]}","Percentage":f"{r[2]}%","Date":r[3]} for r in history],use_container_width=True,hide_index=True)
        st.metric("Best recorded percentage",f"{max(r[2] for r in history)}%")
    else:
        st.info("No saved results yet. Complete a quiz and choose 'Save result to My Progress'.")

st.divider()
st.markdown('<p class="smallnote">JAMBLOOM is an educational guidance tool. It does not guarantee admission or replace official requirements. Verify current information at JAMB IBASS and with your chosen institution.</p>',unsafe_allow_html=True)
