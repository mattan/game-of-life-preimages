# הוראות לפרסום האפליקציה באינטרנט

קובץ זה מכיל הוראות מפורטות לפרסום האפליקציה "מוצא ה-Preimages של משחק החיים" באינטרנט באמצעות Streamlit Cloud.

## פרסום ב-Streamlit Cloud (הדרך המומלצת)

Streamlit Cloud הוא שירות חינמי המאפשר פרסום אפליקציות Streamlit בקלות.

### שלבים לפרסום:

1. **העלאת הפרויקט ל-GitHub**:
   - צור חשבון GitHub אם אין לך
   - צור מאגר (repository) חדש
   - העלה את כל קבצי הפרויקט: `streamlit_app.py`, `requirements.txt` ו-`README.md`

2. **הירשם ל-Streamlit Cloud**:
   - היכנס ל-[Streamlit Cloud](https://streamlit.io/cloud)
   - הירשם באמצעות חשבון GitHub שלך

3. **פרסום האפליקציה**:
   - לחץ על כפתור "New app"
   - בחר את המאגר, הענף והקובץ הראשי (`streamlit_app.py`)
   - לחץ על "Deploy!"
   - המתן מספר דקות לסיום התהליך

4. **שיתוף הקישור**:
   - לאחר הפרסום תקבל קישור ייחודי לאפליקציה
   - שתף את הקישור עם משתמשים אחרים

### הגדרות נוספות (אופציונלי):

- **התאמות עיצוב**: ניתן להוסיף קובץ `.streamlit/config.toml` לתיקייה ולהגדיר בו עיצובים מותאמים אישית
- **סודות**: ניתן להגדיר משתני סביבה מאובטחים בהגדרות האפליקציה ב-Streamlit Cloud
- **זיכרון ומשאבים**: ניתן לשדרג את התוכנית העסקית אם נדרשים משאבים נוספים

## שילוב עם Google Analytics (אופציונלי)

אם ברצונך לעקוב אחר השימוש באפליקציה:

1. צור חשבון Google Analytics וקבל מזהה מעקב
2. הוסף את הקוד הבא ל-`streamlit_app.py`:

```python
st.markdown("""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-ID');
</script>
""", unsafe_allow_html=True)
```

## עדכון האפליקציה

לאחר פרסום האפליקציה, כל פעם שתבצע שינויים במאגר GitHub, האפליקציה תתעדכן אוטומטית.

## פתרון בעיות נפוצות

1. **בעיות בהתקנת חבילות**:
   - ודא שכל החבילות מוגדרות נכון בקובץ `requirements.txt`
   - ודא שגרסאות החבילות תואמות זו לזו

2. **שגיאות זמן ריצה**:
   - בדוק את הלוגים בממשק של Streamlit Cloud
   - תקן שגיאות ובצע push שינויים למאגר

3. **בעיות תצוגה**:
   - בדוק את האפליקציה במכשירים ודפדפנים שונים
   - התאם את העיצוב לפי הצורך באמצעות CSS 