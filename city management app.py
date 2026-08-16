import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from pathlib import Path

# إعدادات الصفحة
st.set_page_config(
    page_title="طلبات إدارة المدينة",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة CSS مخصص
st.markdown("""
    <style>
        .main {
            direction: rtl;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px;
        }
        .stTextInput>div>div>input, .stDateInput>div>div>input, .stSelectbox>div>div>select {
            direction: rtl;
            text-align: right;
        }
        h1, h2, h3, h4, h5, h6 {
            text-align: right;
        }
        .success-box {
            background-color: #d4edda;
            padding: 15px;
            border-radius: 8px;
            border-right: 4px solid #28a745;
            margin: 10px 0;
            text-align: right;
        }
        .error-box {
            background-color: #f8d7da;
            padding: 15px;
            border-radius: 8px;
            border-right: 4px solid #dc3545;
            margin: 10px 0;
            text-align: right;
        }
        .warning-box {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            border-right: 4px solid #ffc107;
            margin: 10px 0;
            text-align: right;
        }
        .metric-box {
            background-color: #e7f3ff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# مسار ملف البيانات
DATA_FILE = "requests_data.json"

# دوال المساعدة
def load_data():
    """تحميل البيانات من الملف"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    """حفظ البيانات في الملف"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_days_overdue(date_str):
    """حساب عدد الأيام المنقضية منذ إنشاء الطلب"""
    request_date = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now()
    delta = today - request_date
    return delta.days

def is_overdue(request):
    """التحقق من تأخر الطلب (أكثر من يومين)"""
    if request['status'] == 'مكتمل':
        return False
    days = calculate_days_overdue(request['created_date'])
    return days > 2

def get_status_color(status):
    """الحصول على لون الحالة"""
    colors = {
        'قيد الانتظار': '🔴',
        'قيد المعالجة': '🟡',
        'مكتمل': '🟢'
    }
    return colors.get(status, '⚪')

# تهيئة الجلسة
if 'requests' not in st.session_state:
    st.session_state.requests = load_data()

# الرأس
st.markdown("<h1 style='text-align: right;'>🏛️ طلبات إدارة المدينة</h1>", unsafe_allow_html=True)
st.divider()

# الإحصائيات
col1, col2, col3, col4 = st.columns(4)

total_requests = len(st.session_state.requests)
pending_requests = len([r for r in st.session_state.requests if r['status'] == 'قيد الانتظار'])
in_progress_requests = len([r for r in st.session_state.requests if r['status'] == 'قيد المعالجة'])
completed_requests = len([r for r in st.session_state.requests if r['status'] == 'مكتمل'])

with col1:
    st.metric("إجمالي الطلبات", total_requests, delta=None)

with col2:
    st.metric("قيد الانتظار", pending_requests, delta=None)

with col3:
    st.metric("قيد المعالجة", in_progress_requests, delta=None)

with col4:
    st.metric("مكتمل", completed_requests, delta=None)

st.divider()

# تبويبات التطبيق
tab1, tab2 = st.tabs(["➕ إضافة طلب جديد", "📋 قائمة الطلبات"])

# التبويب الأول: إضافة طلب جديد
with tab1:
    st.markdown("<h2 style='text-align: right;'>📝 طلب جديد</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        request_type = st.text_input("نوع الطلب", placeholder="مثال: إصلاح الطريق، تنظيف الساحة...")
    
    with col2:
        location = st.text_input("الموقع/المنطقة", placeholder="مثال: شارع النيل، حديقة الملك فهد...")
    
    col3, col4 = st.columns(2)
    
    with col3:
        request_date = st.date_input("التاريخ", datetime.now())
    
    with col4:
        priority = st.selectbox("الأولوية", ["عادي", "مهم", "عاجل"])
    
    col5, col6 = st.columns(2)
    
    with col5:
        request_number = st.text_input("رقم الطلب", placeholder="مثال: 2024-001, REQ-123...")
    
    with col6:
        pass
    
    # زر الإضافة
    if st.button("✅ إضافة الطلب", use_container_width=True, type="primary"):
        # التحقق من الحقول
        if not request_type or not location or not request_number:
            st.markdown("<div class='error-box'>⚠️ يرجى ملء جميع الحقول المطلوبة!</div>", unsafe_allow_html=True)
        elif any(r['request_number'] == request_number for r in st.session_state.requests):
            st.markdown(f"<div class='error-box'>⚠️ رقم الطلب '{request_number}' موجود بالفعل!</div>", unsafe_allow_html=True)
        else:
            # إضافة الطلب الجديد
            new_request = {
                'id': len(st.session_state.requests) + 1,
                'request_number': request_number,
                'request_type': request_type,
                'location': location,
                'priority': priority,
                'status': 'قيد الانتظار',
                'created_date': request_date.strftime("%Y-%m-%d"),
                'created_time': datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.requests.append(new_request)
            save_data(st.session_state.requests)
            st.markdown(f"<div class='success-box'>✅ تم إضافة الطلب رقم '{request_number}' بنجاح!</div>", unsafe_allow_html=True)
            st.balloons()

# التبويب الثاني: قائمة الطلبات
with tab2:
    st.markdown("<h2 style='text-align: right;'>📋 قائمة الطلبات</h2>", unsafe_allow_html=True)
    
    # خيارات التصفية
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("فلترة حسب الحالة", ["الكل", "قيد الانتظار", "قيد المعالجة", "مكتمل"])
    
    with col2:
        filter_priority = st.selectbox("فلترة حسب الأولوية", ["الكل", "عادي", "مهم", "عاجل"])
    
    with col3:
        search_term = st.text_input("ابحث عن طلب", placeholder="رقم الطلب أو النوع أو الموقع...")
    
    st.divider()
    
    # تصفية الطلبات
    filtered_requests = st.session_state.requests.copy()
    
    if filter_status != "الكل":
        filtered_requests = [r for r in filtered_requests if r['status'] == filter_status]
    
    if filter_priority != "الكل":
        filtered_requests = [r for r in filtered_requests if r['priority'] == filter_priority]
    
    if search_term:
        filtered_requests = [r for r in filtered_requests if 
                           search_term.lower() in r['request_number'].lower() or
                           search_term.lower() in r['request_type'].lower() or
                           search_term.lower() in r['location'].lower()]
    
    # ترتيب الطلبات (الطلبات المتأخرة أولاً)
    overdue_requests = [r for r in filtered_requests if is_overdue(r)]
    normal_requests = [r for r in filtered_requests if not is_overdue(r)]
    
    all_sorted_requests = overdue_requests + normal_requests
    
    # عرض الطلبات
    if not all_sorted_requests:
        if len(st.session_state.requests) == 0:
            st.info("ℹ️ لا توجد طلبات حتى الآن. ابدأ بإضافة طلب جديد من التبويب الأول!")
        else:
            st.info("ℹ️ لم يتم العثور على نتائج مطابقة")
    else:
        for request in all_sorted_requests:
            # تحديد اللون بناءً على التأخر
            if is_overdue(request):
                st.markdown(f"""
                <div style='background-color: #ffcccc; padding: 15px; border-radius: 8px; border-right: 4px solid #cc0000; margin: 10px 0;'>
                    <h4 style='color: #cc0000; text-align: right; margin-top: 0;'>⚠️ تنبيه: طلب متأخر جداً! ({calculate_days_overdue(request['created_date'])} أيام)</h4>
                </div>
                """, unsafe_allow_html=True)
            
            # عرض بيانات الطلب
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"<div style='text-align: right;'><strong>رقم الطلب:</strong><br>{request['request_number']}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div style='text-align: right;'><strong>نوع الطلب:</strong><br>{request['request_type']}</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<div style='text-align: right;'><strong>الموقع:</strong><br>{request['location']}</div>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"<div style='text-align: right;'><strong>المدة المنقضية:</strong><br>{calculate_days_overdue(request['created_date'])} أيام</div>", unsafe_allow_html=True)
            
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                priority_emoji = {"عادي": "🔵", "مهم": "🟠", "عاجل": "🔴"}
                st.markdown(f"<div style='text-align: right;'><strong>الأولوية:</strong><br>{priority_emoji.get(request['priority'], '')} {request['priority']}</div>", unsafe_allow_html=True)
            
            with col6:
                status_emoji = get_status_color(request['status'])
                st.markdown(f"<div style='text-align: right;'><strong>الحالة:</strong><br>{status_emoji} {request['status']}</div>", unsafe_allow_html=True)
            
            with col7:
                st.markdown(f"<div style='text-align: right;'><strong>التاريخ:</strong><br>{request['created_date']}</div>", unsafe_allow_html=True)
            
            with col8:
                st.markdown(f"<div style='text-align: right;'><strong>الوقت:</strong><br>{request['created_time']}</div>", unsafe_allow_html=True)
            
            # أزرار التحكم
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if request['status'] != 'قيد الانتظار':
                    if st.button("قيد الانتظار", key=f"waiting_{request['id']}", use_container_width=True):
                        # تحديث الحالة
                        for r in st.session_state.requests:
                            if r['id'] == request['id']:
                                r['status'] = 'قيد الانتظار'
                        save_data(st.session_state.requests)
                        st.rerun()
            
            with col_btn2:
                if request['status'] != 'قيد المعالجة':
                    if st.button("قيد المعالجة", key=f"processing_{request['id']}", use_container_width=True):
                        # تحديث الحالة
                        for r in st.session_state.requests:
                            if r['id'] == request['id']:
                                r['status'] = 'قيد المعالجة'
                        save_data(st.session_state.requests)
                        st.rerun()
            
            with col_btn3:
                if request['status'] != 'مكتمل':
                    if st.button("مكتمل", key=f"completed_{request['id']}", use_container_width=True):
                        # تحديث الحالة
                        for r in st.session_state.requests:
                            if r['id'] == request['id']:
                                r['status'] = 'مكتمل'
                        save_data(st.session_state.requests)
                        st.rerun()
            
            with col_btn4:
                if st.button("🗑️ حذف", key=f"delete_{request['id']}", use_container_width=True):
                    # حذف الطلب
                    st.session_state.requests = [r for r in st.session_state.requests if r['id'] != request['id']]
                    save_data(st.session_state.requests)
                    st.markdown(f"<div class='success-box'>✅ تم حذف الطلب رقم '{request['request_number']}' بنجاح!</div>", unsafe_allow_html=True)
                    st.rerun()
            
            st.divider()

# شريط جانبي
with st.sidebar:
    st.markdown("<h3 style='text-align: right;'>⚙️ الإعدادات</h3>", unsafe_allow_html=True)
    
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.session_state.requests = load_data()
        st.success("✅ تم تحديث البيانات!")
    
    if st.button("🗑️ حذف جميع الطلبات", use_container_width=True):
        if st.checkbox("أنا متأكد من حذف جميع الطلبات"):
            st.session_state.requests = []
            save_data([])
            st.success("✅ تم حذف جميع الطلبات!")
            st.rerun()
    
    st.divider()
    
    st.markdown("<h3 style='text-align: right;'>📊 الإحصائيات</h3>", unsafe_allow_html=True)
    
    # حساب الطلبات المتأخرة
    overdue_count = len([r for r in st.session_state.requests if is_overdue(r)])
    
    if overdue_count > 0:
        st.error(f"⚠️ هناك {overdue_count} طلبات متأخرة!")
    else:
        st.success("✅ لا توجد طلبات متأخرة")
    
    st.divider()
    
    # عرض آخر الطلبات المضافة
    if st.session_state.requests:
        st.markdown("<h3 style='text-align: right;'>📌 آخر الطلبات</h3>", unsafe_allow_html=True)
        for request in st.session_state.requests[-3:]:
            st.markdown(f"**{request['request_number']}** - {request['request_type']}")
