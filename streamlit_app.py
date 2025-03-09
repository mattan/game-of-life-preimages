import streamlit as st
import numpy as np
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import product, combinations as iter_combinations
import time

st.set_page_config(
    page_title="מציאת מצב קודם במשחק החיים",
    page_icon="🧬",
    layout="wide"
)

# CSS לכיוון טקסט מימין לשמאל ועיצוב נוסף
st.markdown("""
<style>
    body {
        direction: rtl;
    }
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
    }
    .alive-cell {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        margin: 2px;
    }
    .dead-cell {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        margin: 2px;
    }
    h1, h2, h3 {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# חלק 1: הכותרת והסבר
st.markdown('<h1 class="rtl">מציאת מצב קודם במשחק החיים בעזרת SAT Solver</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="rtl">
<p>משחק החיים של קונווי הוא אוטומט תאי שבו כל תא יכול להיות במצב חי או מת, ומצבו בדור הבא נקבע לפי מספר השכנים החיים שלו.</p>

<p>חוקי המשחק:</p>
<ol>
    <li>תא חי עם פחות מ-2 שכנים חיים ימות (בדידות)</li>
    <li>תא חי עם 2 או 3 שכנים חיים ישרוד לדור הבא</li>
    <li>תא חי עם יותר מ-3 שכנים חיים ימות (צפיפות)</li>
    <li>תא מת עם בדיוק 3 שכנים חיים יהפוך לחי (רבייה)</li>
</ol>

<p>אפליקציה זו מאפשרת לך לבחור מצב מטרה (תמונה של תאים חיים ומתים), ותמצא עבורך את המצב/ים הקודמ/ים שיובילו אליו.</p>
</div>
""", unsafe_allow_html=True)

# --- פונקציות הליבה מהקוד המקורי ---

def find_preimage(target_state, return_first=True, max_solutions=100, time_limit=30):
    """
    מחפש מצב קודם שיוביל למצב המטרה אחרי צעד אחד במשחק החיים.
    
    Args:
        target_state: מערך דו ממדי NumPy המייצג את מצב המטרה (1 לתאים חיים, 0 לתאים מתים)
        return_first: האם להחזיר רק את הפתרון הראשון (True) או את כל הפתרונות (False)
        max_solutions: מקסימום פתרונות לחפש אם return_first=False
        time_limit: מגבלת זמן בשניות
    
    Returns:
        אם return_first=True: preimage_state מצב קודם כמערך NumPy, או None אם לא נמצא פתרון
        אם return_first=False: רשימה של preimage_states וגם מספר כולל אם יותר מ-max_solutions
    """
    rows, cols = target_state.shape
    
    # יוצר נוסחת CNF
    formula = CNF()
    
    # פונקציית עזר להמרת מיקום תא למספר משתנה
    def cell_to_var(r, c):
        return 1 + r * cols + c
    
    # מכין מיפוי הפוך ממשתנה למיקום תא
    var_to_cell = {}
    for r in range(rows):
        for c in range(cols):
            var_to_cell[cell_to_var(r, c)] = (r, c)
    
    # יוצר אילוצים עבור כל תא במצב המטרה
    for r in range(rows):
        for c in range(cols):
            target_cell = target_state[r, c]
            center_var = cell_to_var(r, c)
            
            # אוסף את כל השכנים האפשריים
            neighbors = []
            for dr, dc in product([-1, 0, 1], [-1, 0, 1]):
                if dr == 0 and dc == 0:  # דילוג על התא עצמו
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbors.append(cell_to_var(nr, nc))
            
            # יוצר אילוצים לפי חוקי משחק החיים
            if target_cell == 1:  # התא חי במצב המטרה
                # מקרה 1: התא היה חי וישרוד לדור הבא (2-3 שכנים)
                # מקרה 2: התא היה מת ונולד בדור הבא (בדיוק 3 שכנים)
                
                # יוצרים את כל המצבים הלא חוקיים ומוסיפים את ההיפוך שלהם
                not_valid_cases = []
                
                # תא חי עם פחות מ-2 שכנים (מת מבדידות)
                for alive_count in range(2):
                    for alive_combo in iter_combinations(neighbors, alive_count):
                        clause = [center_var]  # התא חי
                        for n in neighbors:
                            if n in alive_combo:
                                clause.append(n)  # שכן חי
                            else:
                                clause.append(-n)  # שכן מת
                        not_valid_cases.append(clause)
                
                # תא חי עם יותר מ-3 שכנים (מת מצפיפות)
                for alive_count in range(4, len(neighbors) + 1):
                    for alive_combo in iter_combinations(neighbors, alive_count):
                        clause = [center_var]  # התא חי
                        for n in neighbors:
                            if n in alive_combo:
                                clause.append(n)  # שכן חי
                            else:
                                clause.append(-n)  # שכן מת
                        not_valid_cases.append(clause)
                
                # תא מת שלא בדיוק 3 שכנים (לא נולד)
                for alive_count in range(len(neighbors) + 1):
                    if alive_count != 3:  # כל מקרה חוץ מ-3 שכנים חיים
                        for alive_combo in iter_combinations(neighbors, alive_count):
                            clause = [-center_var]  # התא מת
                            for n in neighbors:
                                if n in alive_combo:
                                    clause.append(n)  # שכן חי
                                else:
                                    clause.append(-n)  # שכן מת
                            not_valid_cases.append(clause)
                
                # הופכים את כל המקרים הלא חוקיים לאילוצי "לפחות אחד מהם חייב להתקיים"
                for clause in not_valid_cases:
                    formula.append([-lit for lit in clause])
                    
            else:  # התא מת במצב המטרה
                # מקרה 1: התא היה חי ומת (פחות מ-2 או יותר מ-3 שכנים)
                # מקרה 2: התא היה מת ונשאר מת (לא בדיוק 3 שכנים)
                
                # יוצרים את כל המצבים הלא חוקיים ומוסיפים את ההיפוך שלהם
                not_valid_cases = []
                
                # תא חי עם 2-3 שכנים (חי בדור הבא - לא מתאים)
                for alive_count in range(2, 4):
                    for alive_combo in iter_combinations(neighbors, alive_count):
                        clause = [center_var]  # התא חי
                        for n in neighbors:
                            if n in alive_combo:
                                clause.append(n)  # שכן חי
                            else:
                                clause.append(-n)  # שכן מת
                        not_valid_cases.append(clause)
                
                # תא מת עם בדיוק 3 שכנים (נולד בדור הבא - לא מתאים)
                for alive_combo in iter_combinations(neighbors, 3):
                    clause = [-center_var]  # התא מת
                    for n in neighbors:
                        if n in alive_combo:
                            clause.append(n)  # שכן חי
                        else:
                            clause.append(-n)  # שכן מת
                    not_valid_cases.append(clause)
                
                # הופכים את כל המקרים הלא חוקיים
                for clause in not_valid_cases:
                    formula.append([-lit for lit in clause])
    
    # פותר את הנוסחה
    solver = Solver(name='glucose4')
    solver.append_formula(formula)
    
    if return_first:
        # רק הפתרון הראשון
        if solver.solve():
            model = solver.get_model()
            
            # המרת המודל בחזרה למצב משחק
            preimage = np.zeros((rows, cols), dtype=int)
            for r in range(rows):
                for c in range(cols):
                    var = cell_to_var(r, c)
                    if var in model:  # חיובי במודל = התא חי
                        preimage[r, c] = 1
            
            solver.delete()
            return preimage
        else:
            solver.delete()
            return None  # אין פתרון
    else:
        # מחפש מספר פתרונות
        solutions = []
        start_time = time.time()
        
        while True:
            # בדיקת מגבלת זמן
            if time.time() - start_time > time_limit:
                break
                
            # פתרון
            if solver.solve():
                model = solver.get_model()
                
                # המרת המודל בחזרה למצב משחק
                preimage = np.zeros((rows, cols), dtype=int)
                for r in range(rows):
                    for c in range(cols):
                        var = cell_to_var(r, c)
                        if var in model:  # חיובי במודל = התא חי
                            preimage[r, c] = 1
                
                solutions.append(preimage.copy())
                
                # מוסיף פסוקית שמונעת חזרה על פתרון זה
                blocking_clause = []
                for var in range(1, rows * cols + 1):
                    if var in model:
                        blocking_clause.append(-var)  # אם var היה 1, כעת הוא צריך להיות 0
                    else:
                        blocking_clause.append(var)   # אם var היה 0, כעת הוא צריך להיות 1
                
                solver.add_clause(blocking_clause)
                
                # בדיקה אם הגענו למספר מקסימלי של פתרונות
                if len(solutions) >= max_solutions:
                    break
            else:
                break
        
        solver.delete()
        return solutions

def next_state(grid):
    """
    מחשב את המצב הבא לפי חוקי משחק החיים
    
    Args:
        grid: מערך דו ממדי NumPy המייצג את המצב הנוכחי
        
    Returns:
        new_grid: מערך דו ממדי NumPy המייצג את המצב הבא
    """
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)
    
    for r in range(rows):
        for c in range(cols):
            # סופר שכנים חיים
            live_neighbors = 0
            for dr, dc in product([-1, 0, 1], [-1, 0, 1]):
                if dr == 0 and dc == 0:
                    continue  # מדלג על התא עצמו
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] == 1:
                    live_neighbors += 1
            
            # מיישם את חוקי משחק החיים
            if grid[r, c] == 1:  # תא חי
                if 2 <= live_neighbors <= 3:
                    new_grid[r, c] = 1  # הישרדות
            else:  # תא מת
                if live_neighbors == 3:
                    new_grid[r, c] = 1  # לידה
    
    return new_grid

# --- ממשק משתמש של Streamlit ---

st.markdown('<h2 class="rtl">בחר את מצב המטרה</h2>', unsafe_allow_html=True)

# סלקטור לבחירת גודל הלוח (3x3 עד 8x8)
col1, col2 = st.columns([1, 3])
with col1:
    grid_size = st.slider("גודל הלוח:", min_value=3, max_value=8, value=5, step=1)

with col2:
    st.markdown("""
    <div class="rtl">
    <p>בחר גודל לוח והגדר את מצב המטרה על ידי לחיצה על התאים שברצונך שיהיו חיים (צבועים בירוק). לאחר מכן, לחץ על כפתור "מצא מצב קודם" כדי לחשב את המצב הקודם.</p>
    <p>מצב "גן עדן" הוא מצב שלא ניתן להגיע אליו מאף מצב קודם.</p>
    </div>
    """, unsafe_allow_html=True)

# יצירת לוח אינטראקטיבי
st.markdown('<div class="rtl">לחץ על תאים כדי לסמן אותם כ"חיים":</div>', unsafe_allow_html=True)

# מסדר את הנתונים בתוך לוח (מטריצה)
if 'grid_data' not in st.session_state:
    st.session_state.grid_data = np.zeros((8, 8), dtype=int)  # מקסימום 8x8

# עדכון גודל הנתונים אם משתנה גודל הלוח
if st.session_state.grid_data.shape[0] != grid_size:
    # שומר את הנתונים הקיימים אם הלוח גדל
    temp = np.zeros((grid_size, grid_size), dtype=int)
    min_rows = min(grid_size, st.session_state.grid_data.shape[0])
    min_cols = min(grid_size, st.session_state.grid_data.shape[1])
    temp[:min_rows, :min_cols] = st.session_state.grid_data[:min_rows, :min_cols]
    st.session_state.grid_data = temp

# מציג את הלוח כרשת של כפתורים
for r in range(grid_size):
    cols = st.columns(grid_size)
    for c in range(grid_size):
        with cols[c]:
            key = f"cell_{r}_{c}"
            if st.button(
                "⬤" if st.session_state.grid_data[r, c] == 1 else "○", 
                key=key,
                help=f"תא בשורה {r+1}, עמודה {c+1}"
            ):
                # מחליף את מצב התא בין חי למת
                st.session_state.grid_data[r, c] = 1 - st.session_state.grid_data[r, c]
                st.rerun()

# כפתורים לשליטה במצב הלוח
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("נקה הכל"):
        st.session_state.grid_data = np.zeros((grid_size, grid_size), dtype=int)
        st.rerun()
with col2:
    if st.button("מלא אקראית"):
        st.session_state.grid_data = np.random.randint(0, 2, (grid_size, grid_size))
        st.rerun()
with col3:
    if st.button("הפוך הכל"):
        st.session_state.grid_data = 1 - st.session_state.grid_data
        st.rerun()

# דוגמאות מוכנות מראש
st.markdown('<h3 class="rtl">או בחר דוגמה מוכנה:</h3>', unsafe_allow_html=True)

examples_col1, examples_col2, examples_col3, examples_col4 = st.columns(4)

# דוגמה 1: בלינקר (קו אנכי)
with examples_col1:
    if st.button("בלינקר (אנכי)"):
        if grid_size >= 3:
            st.session_state.grid_data = np.zeros((grid_size, grid_size), dtype=int)
            st.session_state.grid_data[grid_size//2-1:grid_size//2+2, grid_size//2] = 1
            st.rerun()
        else:
            st.error("נדרש לוח בגודל 3x3 לפחות")

# דוגמה 2: בלינקר (קו אופקי)
with examples_col2:
    if st.button("בלינקר (אופקי)"):
        if grid_size >= 3:
            st.session_state.grid_data = np.zeros((grid_size, grid_size), dtype=int)
            st.session_state.grid_data[grid_size//2, grid_size//2-1:grid_size//2+2] = 1
            st.rerun()
        else:
            st.error("נדרש לוח בגודל 3x3 לפחות")

# דוגמה 3: בלוק 2x2
with examples_col3:
    if st.button("בלוק 2x2"):
        if grid_size >= 4:
            st.session_state.grid_data = np.zeros((grid_size, grid_size), dtype=int)
            st.session_state.grid_data[grid_size//2-1:grid_size//2+1, grid_size//2-1:grid_size//2+1] = 1
            st.rerun()
        else:
            st.error("נדרש לוח בגודל 4x4 לפחות")

# דוגמה 4: מצב גן עדן
with examples_col4:
    if st.button("מצב גן עדן"):
        if grid_size >= 5:
            st.session_state.grid_data = np.zeros((grid_size, grid_size), dtype=int)
            # מייצר תבנית מורכבת שסביר שהיא גן עדן
            pattern = np.array([
                [1, 1, 0, 1, 1],
                [1, 0, 0, 1, 0],
                [0, 0, 0, 0, 0],
                [1, 1, 0, 1, 1],
                [1, 0, 0, 1, 0]
            ])
            st.session_state.grid_data[:5, :5] = pattern
            st.rerun()
        else:
            st.error("נדרש לוח בגודל 5x5 לפחות")

# הדפסת המטריצה הנוכחית
target_matrix = st.session_state.grid_data[:grid_size, :grid_size].copy()

# הדפסת מצב המטריצה אם יש צורך לדבג
# st.write("מצב נוכחי של המטריצה:")
# st.write(target_matrix)

# כפתור לחיפוש מצב קודם
st.markdown("<hr>", unsafe_allow_html=True)
if st.button("מצא מצב קודם", type="primary"):
    if np.sum(target_matrix) == 0:
        st.warning("הלוח ריק. אנא בחר לפחות תא אחד כ'חי'.")
    else:
        with st.spinner("מחפש את המצב הקודם..."):
            max_solutions_to_find = 10
            time_limit_seconds = 10
            
            # מציג את הספירה לאחור
            progress_text = "חיפוש פתרון בעזרת SAT Solver..."
            progress_bar = st.progress(0)
            
            solutions = []
            solutions = find_preimage(
                target_matrix, 
                return_first=False, 
                max_solutions=max_solutions_to_find,
                time_limit=time_limit_seconds
            )
            
            progress_bar.progress(100)
        
        # הדפסת התוצאות
        if solutions and len(solutions) > 0:
            st.success(f"נמצאו {len(solutions)} פתרונות!")
            st.markdown('<h2 class="rtl">התוצאות:</h2>', unsafe_allow_html=True)
            
            # מציג מספר פתרונות ראשונים
            for i, solution in enumerate(solutions[:5]):
                st.markdown(f'<h3 class="rtl">פתרון {i+1}:</h3>', unsafe_allow_html=True)
                
                # הצגה גרפית של הפתרון
                for r in range(grid_size):
                    cols = st.columns(grid_size)
                    for c in range(grid_size):
                        with cols[c]:
                            if solution[r, c] == 1:
                                st.markdown('<div class="alive-cell">⬤</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="dead-cell">○</div>', unsafe_allow_html=True)
                
                # אימות הפתרון
                next_gen = next_state(solution)
                is_valid = np.array_equal(next_gen, target_matrix)
                
                if is_valid:
                    st.success("✓ פתרון תקף! המצב הבא של פתרון זה תואם את מצב המטרה.")
                else:
                    st.error("✗ פתרון לא תקף! המצב הבא של פתרון זה אינו תואם את מצב המטרה.")
                
                st.markdown("<hr>", unsafe_allow_html=True)
            
            if len(solutions) > 5:
                st.info(f"קיימים עוד {len(solutions) - 5} פתרונות נוספים שלא מוצגים כאן.")
        else:
            st.error("""
            לא נמצא מצב קודם למצב המטרה!
            
            זהו כנראה מצב "גן עדן" (Garden of Eden) - מצב שלא יכול להתקבל מאף מצב קודם לפי חוקי משחק החיים.
            """)

# מידע נוסף
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("מידע נוסף על היישום"):
    st.markdown("""
    <div class="rtl">
    <h3>איך זה עובד?</h3>
    <p>מציאת מצב קודם במשחק החיים היא בעיה מורכבת שניתן לפתור באמצעות Boolean Satisfiability (SAT).</p>
    
    <p>האלגוריתם פועל כך:</p>
    <ol>
        <li>מייצג כל תא כמשתנה בוליאני</li>
        <li>יוצר אילוצים שמבטיחים שחוקי משחק החיים מובילים מהמצב הקודם למצב המטרה</li>
        <li>משתמש ב-SAT Solver כדי למצוא פתרון לאילוצים</li>
        <li>ממיר את הפתרון בחזרה למצב המשחק</li>
    </ol>
    
    <p>בנוסף, חשוב לציין שיש מצבים שלא ניתן להגיע אליהם מאף מצב קודם - אלו הם מצבי "גן עדן" המפורסמים במשחק החיים.</p>
    
    <h3>הגבלות:</h3>
    <ul>
        <li>חיפוש הפתרון מוגבל ל-10 פתרונות לכל היותר</li>
        <li>החיפוש מוגבל ל-10 שניות</li>
        <li>האלגוריתם עשוי שלא למצוא פתרון עבור לוחות גדולים מדי</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# תחתית הדף
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class="rtl" style="text-align: center; color: #888;">
נבנה עם <a href="https://streamlit.io" target="_blank">Streamlit</a> ו-<a href="https://pysathq.github.io/" target="_blank">PySAT</a> | משחק החיים של קונווי
</div>
""", unsafe_allow_html=True) 