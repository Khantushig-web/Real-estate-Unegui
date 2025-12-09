import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
import re
import math

# Page config
st.set_page_config(
    page_title="Ulaanbaatar Real Estate Map",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stMetric {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stSelectbox, .stSlider {
        background: white;
        padding: 10px;
        border-radius: 8px;
    }
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    h2, h3 {
        color: #1e40af;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    .filter-section {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Language toggle
if 'language' not in st.session_state:
    st.session_state.language = 'mn'

# Translation dictionary
TRANSLATIONS = {
    'mn': {
        'title': '🏠 Улаанбаатар Үл Хөдлөх Хөрөнгийн Зураг',
        'subtitle': 'unegui.mn-ээс авсан бодит зарууд',
        'filters': '🔍 Шүүлтүүр',
        'district': 'Дүүрэг',
        'all': 'Бүгд',
        'price_range': 'Үнийн хязгаар',
        'area': 'Талбай (м²)',
        'balcony': 'Тагт',
        'balcony_count': 'Тагтны тоо',
        'elevator': 'Лифт',
        'garage': 'Гараж',
        'door': 'Хаалга',
        'floor_type': 'Шал',
        'rooms': 'Өрөөний тоо',
        'yes': 'Тийм',
        'no': 'Үгүй',
        'any': 'Аль ч',
        'year': 'Баригдсан он',
        'window_count': 'Цонхны тоо',
        'showing': 'Нийт',
        'properties': 'зар',
        'avg_price': 'Дундаж үнэ',
        'median_price': 'Дунд үнэ',
        'avg_area': 'Дундаж талбай',
        'total_listings': 'Нийт зар',
        'map_title': '🗺️ Интерактив зураг',
        'property_list': '📋 Зарын жагсаалт',
        'floor': 'Давхар',
        'location': 'Байршил',
        'features': 'Онцлог',
        'description': 'Тайлбар',
        'view_on': 'unegui.mn дээр харах',
        'date': 'Огноо',
        'views': 'үзсэн',
        'loading': 'Зарууд ачаалж байна...',
        'loaded': '✓ unegui.mn-ээс',
        'filter_info': 'ℹ️ 10 саяас доош үнийг талбайгаар үржүүлсэн.',
        'price_legend': 'Үнийн заагч',
        'million': 'сая',
        'billion': 'тэрбум',
        'no_results': '⚠️ Таны шүүлтүүрт тохирох зар олдсонгүй. Шүүлтүүрийг өөрчилнө үү.',
        'basic_filters': '📊 Үндсэн шүүлтүүр',
        'feature_filters': '✨ Онцлог шүүлтүүр',
        'apply_filters': 'Шүүлтүүр хэрэглэх',
        'mortgage_title': '🧮 Ипотекийн тооцоолуур',
        'mortgage_price': 'Үл хөдлөхийн үнэ (₮)',
        'mortgage_down_pct': 'Урьдчилгаа %',
        'mortgage_rate': 'Ипотекийн хүү % (МБ)',
        'mortgage_budget': 'Таны сар бүр төлөх боломжит төлбөр (₮)',
        'mortgage_loan_zero': 'Зээлийн дүн 0 байна. Үнийг өсгөх эсвэл урьдчилгааны хувийг бууруулна уу.',
        'mortgage_rate_zero': 'Хүү 0-ээс их байх ёстой.',
        'mortgage_budget_zero': 'Сарын төлбөрөө 0-ээс их утгаар оруулна уу.',
        'mortgage_budget_low': 'Таны сарын төлбөр бага байна. Доорх хугацаа нь хүүг тооцоогүй ойролцоо тооцоо юм.',
        'mortgage_result_time': '🏦 Төлбөр дуусах хугацаа',
        'mortgage_result_total': '💰 Нийт төлөх дүн (урьдчилгаа оруулаад)',
        'mortgage_hint': '➡️ Сонгосон зарыг хараад үнийг энд хуулж тавиад ипотекийн хугацаагаа тооцоолно уу.'
    },
    'en': {
        'title': '🏠 Ulaanbaatar Real Estate Map',
        'subtitle': 'Real property listings from unegui.mn',
        'filters': '🔍 Filters',
        'district': 'District',
        'all': 'All',
        'price_range': 'Price Range',
        'area': 'Area (m²)',
        'balcony': 'Balcony',
        'balcony_count': 'Balconies',
        'elevator': 'Elevator',
        'garage': 'Garage',
        'door': 'Door Type',
        'floor_type': 'Floor Type',
        'rooms': 'Rooms',
        'yes': 'Yes',
        'no': 'No',
        'any': 'Any',
        'year': 'Built Year',
        'window_count': 'Windows',
        'showing': 'Showing',
        'properties': 'properties',
        'avg_price': 'Average Price',
        'median_price': 'Median Price',
        'avg_area': 'Avg Area',
        'total_listings': 'Total Listings',
        'map_title': '🗺️ Interactive Map',
        'property_list': '📋 Property Listings',
        'floor': 'Floor',
        'location': 'Location',
        'features': 'Features',
        'description': 'Description',
        'view_on': 'View on unegui.mn',
        'date': 'Date',
        'views': 'views',
        'loading': 'Loading properties...',
        'loaded': '✓ Loaded',
        'filter_info': 'ℹ️ Prices under 10M treated as price/m².',
        'price_legend': 'Price Legend',
        'million': 'M',
        'billion': 'B',
        'no_results': '⚠️ No properties match your filters. Please adjust the criteria.',
        'basic_filters': '📊 Basic Filters',
        'feature_filters': '✨ Feature Filters',
        'apply_filters': 'Apply Filters',
        'mortgage_title': '🧮 Mortgage calculator',
        'mortgage_price': 'Property price (₮)',
        'mortgage_down_pct': 'Down payment %',
        'mortgage_rate': 'Mortgage interest %',
        'mortgage_budget': 'Your monthly payment budget (₮)',
        'mortgage_loan_zero': 'Loan amount is zero. Increase price or decrease down payment %.',
        'mortgage_rate_zero': 'Interest rate must be greater than 0.',
        'mortgage_budget_zero': 'Please enter a monthly payment greater than 0.',
        'mortgage_budget_low': 'Your monthly budget is very low; the estimate below ignores interest and is only approximate.',
        'mortgage_result_time': '🏦 Payoff time',
        'mortgage_result_total': '💰 Total paid (including down payment)',
        'mortgage_hint': '➡️ Choose a listing, copy its price here and calculate your mortgage duration.'
    }
}

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# Header with language toggle
col1, col2 = st.columns([6, 1])
with col1:
    st.title(t('title'))
    st.markdown(f"**{t('subtitle')}**")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🌐 MN" if st.session_state.language == 'en' else "🌐 EN", use_container_width=True):
        st.session_state.language = 'en' if st.session_state.language == 'mn' else 'mn'
        st.rerun()

@st.cache_data
def load_unegui_data():
    """Load and process the scraped unegui.mn data"""

    def clean_date_text(val):
        """Remove 'unuudur/өнөөдөр' etc from date text"""
        if val is None or val == 'nan' or pd.isna(val):
            return ''
        s = str(val)
        for w in ['Өнөөдөр', 'өнөөдөр', 'unuudur', 'unuudur']:
            s = s.replace(w, '')
        return s.strip()

    try:
        df = pd.read_csv('unegui_data.csv')
    except Exception:
        return pd.DataFrame(columns=[
            'id', 'title', 'price', 'district', 'area', 'balcony', 'elevator',
            'garage', 'year', 'window_count', 'door', 'floor_type', 'rooms'
        ])

    processed = []

    for idx, row in df.iterrows():
        try:
            area_str = str(row.get('Area', ''))
            area_match = re.findall(r'[\d.]+', area_str)
            area = float(area_match[0]) if area_match else 0
            # drop 0 m2 and crazy outliers like 7248m2
            if area == 0 or area > 1000:
                continue

            price_str = str(row.get('Price', '') or row.get('Price(0)', ''))
            price_matches = re.findall(r'[\d,]+', price_str)
            if price_matches:
                prices = [int(p.replace(',', '')) for p in price_matches]
                price = min(prices)
                if 'тэрбум' in price_str.lower() or 'тэрбүм' in price_str.lower():
                    if price < 100:
                        price *= 1_000_000_000
                elif price < 1000:
                    price *= 1_000_000
            else:
                price = 0

            if price <= 10_000_000:
                price *= area
            elif 10_000_000 < price < 20_000_000:
                continue

            image_str = str(row.get('images', '') or row.get('Image', ''))
            image_match = re.findall(r'https?://[^\s"\']+', image_str)
            image_url = image_match[0] if image_match else ''
            if image_url:
                image_url = image_url.split()[0].rstrip(',;')

            location = str(row.get('Location', '') or row.get('Place', '') or row.get('Location Detail', ''))
            district = extract_district(location)

            balcony = str(row.get('Balcony', '')).strip()
            balcony_count = None
            if balcony:
                nums = re.findall(r'\d+', balcony)
                if nums:
                    try:
                        balcony_count = int(nums[0])
                    except ValueError:
                        balcony_count = None
                else:
                    bl = balcony.lower()
                    if 'тагтгүй' in bl or 'тагт гүй' in bl or 'no' in bl:
                        balcony_count = 0

            elevator = str(row.get('Elevator', '')).strip()
            garage = str(row.get('Garage', '')).strip()
            window_count = str(row.get('Window Count', '') or row.get('Window', '')).strip()
            year = str(row.get('Commissioning Year', '')).strip()

            door = str(row.get('Door Type', '') or row.get('Door', '')).strip()
            floor_type = str(row.get('Floor Type', '') or row.get('Floor_Type', '') or row.get('Floor', '')).strip()
            rooms = str(row.get('Room Count', '') or row.get('Rooms', '')).strip()

            coords = get_district_coordinates(district, idx)

            if price > 0 and coords:
                processed.append({
                    'id': idx,
                    'title': str(row.get('Title', '') or row.get('Title(0)', 'Property')),
                    'price': price,
                    'price_formatted': format_price(price, 'mn'),
                    'location': location,
                    'district': district,
                    'area': area,
                    'floor': str(row.get('Floor Number', '')),
                    'building_floor': str(row.get('Building Floor', '')),
                    'year': year,
                    'balcony': balcony,
                    'balcony_count': balcony_count,
                    'elevator': elevator,
                    'garage': garage,
                    'window_count': window_count,
                    'door': door,
                    'floor_type': floor_type,
                    'rooms': rooms,
                    'description': str(row.get('Description', ''))[:300],
                    'date': str(row.get('Published Date', '') or row.get('Date', '')),
                    'views': str(row.get('View Count', '')),
                    'image_url': image_url,
                    'link': str(row.get('Title link', '') or row.get('Link', '')),
                    'lat': coords['lat'],
                    'lng': coords['lng']
                })
        except Exception:
            continue

    result_df = pd.DataFrame(processed)

    if len(result_df) > 0:
        result_df = result_df.drop_duplicates(
            subset=['title', 'price', 'area'],
            keep='first'
        )

    required_columns = [
        'year', 'garage', 'elevator', 'balcony', 'balcony_count',
        'window_count', 'door', 'floor_type', 'rooms', 'price', 'area',
        'district', 'date', 'link'
    ]
    for col in required_columns:
        if col not in result_df.columns:
            result_df[col] = None

    # clean dates (remove 'unuudur/өнөөдөр')
    result_df['date'] = result_df['date'].apply(clean_date_text)

    return result_df

def clean_date_text(val):
    if val is None or val == 'nan' or pd.isna(val):
        return ''
    s = str(val)
    for w in ['Өнөөдөр', 'өнөөдөр', 'unuudur', 'unuudur']:
        s = s.replace(w, '')
    return s.strip()

def extract_district(location):
    districts = {
        'Сүхбаатар': 'Sukhbaatar', 'Sukhbaatar': 'Sukhbaatar', 'СХД': 'Sukhbaatar',
        'Хан-Уул': 'Khan-Uul', 'Khan-Uul': 'Khan-Uul', 'ХУД': 'Khan-Uul',
        'Чингэлтэй': 'Chingeltei', 'Chingeltei': 'Chingeltei', 'ЧД': 'Chingeltei',
        'Баянзүрх': 'Bayanzurkh', 'Bayanzurkh': 'Bayanzurkh', 'БЗД': 'Bayanzurkh',
        'Сонгинохайрхан': 'Songino Khairkhan', 'Songino Khairkhan': 'Songino Khairkhan',
        'Баянгол': 'Bayangol', 'Bayangol': 'Bayangol', 'БГД': 'Bayangol'
    }
    for key, value in districts.items():
        if key in location:
            return value
    return 'Unknown'

def get_district_coordinates(district, seed):
    import random
    random.seed(seed)
    district_centers = {
        'Sukhbaatar': (47.9184, 106.9177),
        'Khan-Uul': (47.8908, 106.9536),
        'Chingeltei': (47.9245, 106.9034),
        'Bayanzurkh': (47.9066, 107.0044),
        'Songino Khairkhan': (47.9089, 106.8041),
        'Bayangol': (47.9078, 106.8637),
        'Unknown': (47.9184, 106.9177)
    }
    center = district_centers.get(district, district_centers['Unknown'])
    lat_offset = random.uniform(-0.025, 0.025)
    lng_offset = random.uniform(-0.025, 0.025)
    return {'lat': center[0] + lat_offset, 'lng': center[1] + lng_offset}

def format_price(price, lang='mn'):
    USD_RATE = 3400
    if lang == 'mn':
        if price >= 1_000_000_000:
            return f"₮{price/1_000_000_000:.1f} тэрбум"
        elif price >= 1_000_000:
            return f"₮{price/1_000_000:.0f} сая"
        else:
            return f"₮{price:,.0f}"
    else:
        usd = price / USD_RATE
        if usd >= 1_000_000:
            return f"${usd/1_000_000:.2f}M"
        elif usd >= 1_000:
            return f"${usd/1_000:.0f}K"
        else:
            return f"${usd:.0f}"

def get_marker_color(price):
    if price < 200_000_000:
        return 'green'
    elif price < 400_000_000:
        return 'blue'
    elif price < 600_000_000:
        return 'orange'
    else:
        return 'red'

def has_feature(value):
    if not value or value == 'nan' or value == '' or pd.isna(value):
        return False
    v = str(value).lower()
    return 'тийм' in v or 'байгаа' in v or 'yes' in v or 'тайлбар' in v

def is_elevator_yes(value):
    if not value or value == 'nan' or value == '' or pd.isna(value):
        return False
    v = str(value).strip().lower()
    return 'shattai' in v or 'шаттай' in v

def is_elevator_no(value):
    if not value or value == 'nan' or value == '' or pd.isna(value):
        return False
    v = str(value).strip().lower()
    return 'shatgui' in v or 'шатгүй' in v

# Load data
with st.spinner(t('loading')):
    df = load_unegui_data()

if len(df) == 0:
    st.error("No data available. Please check your data file.")
    st.stop()

st.success(f"{t('loaded')} {len(df)} {t('properties')}")
st.info(t('filter_info'))

# Sidebar filters
st.sidebar.markdown(f"<div class='filter-section'><h2>{t('filters')}</h2></div>", unsafe_allow_html=True)

# BASIC FILTERS
st.sidebar.markdown(f"### {t('basic_filters')}")

districts_available = sorted(df['district'].unique().tolist())
selected_districts = st.sidebar.multiselect(
    t('district'),
    districts_available,
    default=districts_available,
    help="Select one or more districts"
)

# if no district chosen -> stop with message
if not selected_districts:
    if st.session_state.language == 'mn':
        st.warning("Дүүрэг сонгоно уу.")
    else:
        st.warning("Please choose a district.")
    st.stop()

min_price = int(df['price'].min()) if not df.empty else 0
max_price = int(df['price'].max()) if not df.empty else 1_000_000
min_price_display = min_price / 1_000_000
max_price_display = max_price / 1_000_000

price_range_display = st.sidebar.slider(
    f"{t('price_range')} ({t('million')})",
    float(min_price_display),
    float(max_price_display),
    (float(min_price_display), float(max_price_display)),
    step=1.0
)
price_range = (int(price_range_display[0] * 1_000_000),
               int(price_range_display[1] * 1_000_000))

max_area = float(df['area'].max()) if not df.empty else 1000.0
if max_area > 0:
    area_range = st.sidebar.slider(
        t('area'),
        0.0,
        max_area,
        (0.0, max_area)
    )
else:
    area_range = (0.0, 1000.0)

years = df['year'].unique()
years_numeric = [int(y) for y in years if y and y != 'nan' and str(y).isdigit()]
if years_numeric:
    min_year = min(years_numeric)
    max_year = max(years_numeric)
    year_range = st.sidebar.slider(
        t('year'),
        min_year,
        max_year,
        (min_year, max_year)
    )
else:
    year_range = (1990, 2025)

# FEATURE FILTERS
st.sidebar.markdown(f"### {t('feature_filters')}")

elevator_filter = st.sidebar.selectbox(t('elevator'), [t('any'), t('yes'), t('no')])
garage_filter = st.sidebar.selectbox(t('garage'), [t('any'), t('yes'), t('no')])

unique_doors = sorted([x for x in df['door'].unique() if x and str(x) != 'nan'])
door_options = [t('any')] + unique_doors
door_filter = st.sidebar.selectbox(t('door'), door_options)

unique_floors = sorted([x for x in df['floor_type'].unique() if x and str(x) != 'nan'])
floor_options = [t('any')] + unique_floors
floor_filter = st.sidebar.selectbox(t('floor_type'), floor_options)

# ROOMS slider
rooms_range = None
rooms_has_data = False
if 'rooms' in df.columns:
    rooms_extracted = df['rooms'].astype(str).str.extract(r'(\d+)')[0]
    rooms_numeric = pd.to_numeric(rooms_extracted, errors='coerce')
    if not rooms_numeric.dropna().empty:
        rooms_has_data = True
        min_rooms = int(rooms_numeric.min())
        max_rooms = int(rooms_numeric.max())
    else:
        min_rooms, max_rooms = 1, 5
    rooms_range = st.sidebar.slider(
        t('rooms'),
        min_value=min_rooms,
        max_value=max_rooms,
        value=(min_rooms, max_rooms),
        step=1
    )

# BALCONIES slider
balcony_range = None
if 'balcony_count' in df.columns:
    balcony_numbers = pd.to_numeric(df['balcony_count'], errors='coerce').dropna()
    if not balcony_numbers.empty:
        min_b = int(balcony_numbers.min())
        max_b = int(balcony_numbers.max())
        if min_b < max_b:
            balcony_range = st.sidebar.slider(
                t('balcony_count'),
                min_value=min_b,
                max_value=max_b,
                value=(min_b, max_b),
                step=1
            )
        else:
            st.sidebar.info(f"{t('balcony_count')}: {min_b}")

# WINDOWS slider
window_range = None
windows_has_data = False
if 'window_count' in df.columns:
    windows_extracted = df['window_count'].astype(str).str.extract(r'(\d+)')[0]
    windows_numeric = pd.to_numeric(windows_extracted, errors='coerce')
    if not windows_numeric.dropna().empty:
        windows_has_data = True
        min_w = int(windows_numeric.min())
        max_w = int(windows_numeric.max())
    else:
        min_w, max_w = 1, 6
    window_range = st.sidebar.slider(
        t('window_count'),
        min_value=min_w,
        max_value=max_w,
        value=(min_w, max_w),
        step=1
    )

# APPLY FILTERS
filtered_df = df.copy()

if selected_districts:
    filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]

filtered_df = filtered_df[
    (filtered_df['price'] >= price_range[0]) &
    (filtered_df['price'] <= price_range[1]) &
    (filtered_df['area'] >= area_range[0]) &
    (filtered_df['area'] <= area_range[1])
]

if elevator_filter == t('yes'):
    filtered_df = filtered_df[filtered_df['elevator'].apply(is_elevator_yes)]
elif elevator_filter == t('no'):
    filtered_df = filtered_df[filtered_df['elevator'].apply(is_elevator_no)]

if garage_filter == t('yes'):
    filtered_df = filtered_df[filtered_df['garage'].apply(has_feature)]
elif garage_filter == t('no'):
    filtered_df = filtered_df[~filtered_df['garage'].apply(has_feature)]

if door_filter != t('any'):
    filtered_df = filtered_df[filtered_df['door'] == door_filter]

if floor_filter != t('any'):
    filtered_df = filtered_df[filtered_df['floor_type'] == floor_filter]

if rooms_range is not None and rooms_has_data:
    rooms_extracted_f = filtered_df['rooms'].astype(str).str.extract(r'(\d+)')[0]
    rooms_numeric_f = pd.to_numeric(rooms_extracted_f, errors='coerce')
    mask_rooms = (rooms_numeric_f >= rooms_range[0]) & (rooms_numeric_f <= rooms_range[1])
    filtered_df = filtered_df[mask_rooms.fillna(False)]

if balcony_range is not None and 'balcony_count' in filtered_df.columns:
    balcony_num_f = pd.to_numeric(filtered_df['balcony_count'], errors='coerce')
    filtered_df = filtered_df[
        (balcony_num_f >= balcony_range[0]) &
        (balcony_num_f <= balcony_range[1])
    ]

if 'year' in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df['year'].apply(
            lambda y: str(y).isdigit() and year_range[0] <= int(y) <= year_range[1]
            if y and y != 'nan' else True
        )
    ]

if window_range is not None and windows_has_data:
    windows_extracted_f = filtered_df['window_count'].astype(str).str.extract(r'(\d+)')[0]
    windows_numeric_f = pd.to_numeric(windows_extracted_f, errors='coerce')
    mask_windows = (windows_numeric_f >= window_range[0]) & (windows_numeric_f <= window_range[1])
    filtered_df = filtered_df[mask_windows.fillna(False)]

# Sidebar summary
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<h3 style='text-align: center; color: #667eea;'>{t('showing')} {len(filtered_df)} {t('properties')}</h3>",
    unsafe_allow_html=True
)

# TOP STATS
col1, col2, col3, col4 = st.columns(4)
if len(filtered_df) > 0:
    with col1:
        st.metric(t('avg_price'), format_price(filtered_df['price'].mean(), st.session_state.language))
    with col2:
        st.metric(t('median_price'), format_price(filtered_df['price'].median(), st.session_state.language))
    with col3:
        avg_area = filtered_df['area'].mean() if filtered_df['area'].sum() > 0 else 0
        st.metric(t('avg_area'), f"{avg_area:.0f}m²")
    with col4:
        st.metric(t('total_listings'), len(filtered_df))
else:
    with col1:
        st.metric(t('avg_price'), "N/A")
    with col2:
        st.metric(t('median_price'), "N/A")
    with col3:
        st.metric(t('avg_area'), "N/A")
    with col4:
        st.metric(t('total_listings'), "0")

st.markdown("<br>", unsafe_allow_html=True)

# ------------- MORTGAGE CALCULATOR -------------
st.subheader(t('mortgage_title'))

default_price = int(filtered_df['price'].median()) if len(filtered_df) > 0 else 300_000_000

calc_c1, calc_c2, calc_c3 = st.columns(3)
with calc_c1:
    price_input = st.number_input(
        t('mortgage_price'),
        min_value=0,
        value=int(default_price),
        step=1_000_000
    )
with calc_c2:
    down_pct = st.number_input(
        t('mortgage_down_pct'),
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=1.0
    )
with calc_c3:
    rate_annual = st.number_input(
        t('mortgage_rate'),
        min_value=0.0,
        max_value=30.0,
        value=8.0,
        step=0.1
    )

monthly_budget = st.number_input(
    t('mortgage_budget'),
    min_value=0.0,
    value=2_000_000.0,
    step=100_000.0
)

loan_amount = price_input * (1 - down_pct / 100)

if loan_amount <= 0:
    st.info(t('mortgage_loan_zero'))
else:
    r = rate_annual / 100 / 12
    if r <= 0:
        st.info(t('mortgage_rate_zero'))
    elif monthly_budget <= 0:
        st.info(t('mortgage_budget_zero'))
    else:
        min_payment = loan_amount * r
        if monthly_budget > min_payment:
            # normal amortization
            n_months = -math.log(1 - loan_amount * r / monthly_budget) / math.log(1 + r)
            years = n_months / 12
            total_paid = monthly_budget * n_months + price_input * (down_pct / 100)
            if st.session_state.language == 'mn':
                duration_text = f"{years:.1f} жил ({n_months:.0f} сар)"
            else:
                duration_text = f"{years:.1f} years ({n_months:.0f} months)"
            st.write(f"{t('mortgage_result_time')}: **{duration_text}**")
            st.write(f"{t('mortgage_result_total')}: **₮{total_paid:,.0f}**")
        else:
            # budget too low -> approximate ignoring interest
            st.warning(t('mortgage_budget_low'))
            n_months = loan_amount / monthly_budget
            years = n_months / 12
            total_paid = monthly_budget * n_months + price_input * (down_pct / 100)
            if st.session_state.language == 'mn':
                duration_text = f"{years:.1f} жил ({n_months:.0f} сар)"
            else:
                duration_text = f"{years:.1f} years ({n_months:.0f} months)"
            st.write(f"{t('mortgage_result_time')}: **{duration_text}**")
            st.write(f"{t('mortgage_result_total')}: **₮{total_paid:,.0f}**")

st.caption(t('mortgage_hint'))

st.markdown("<br>", unsafe_allow_html=True)

# ------------- MAP -------------
st.subheader(t('map_title'))

if len(filtered_df) > 0:
    m = folium.Map(
        location=[47.9184, 106.9177],
        zoom_start=11,
        tiles='OpenStreetMap'
    )

    marker_cluster = plugins.MarkerCluster(
        name="Properties",
        overlay=True,
        control=True
    ).add_to(m)

    for idx, row in filtered_df.iterrows():
        # make title clickable if link exists
        if row['link'] and row['link'] != 'nan':
            title_html = f"<a href='{row['link']}' target='_blank' style='color:#1e40af;text-decoration:none;'>{row['title']}</a>"
        else:
            title_html = row['title']

        popup_html = f"""
        <div style="width: 350px; font-family: Arial;">
            <h3 style="margin: 0 0 12px 0; color: #1e40af; font-size: 16px;">{title_html}</h3>
        """
        if row['image_url'] and row['image_url'] != 'nan':
            popup_html += f"""
            <div style="margin-bottom: 12px;">
                <img src="{row['image_url']}"
                     style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;"
                     onerror="this.parentElement.style.display='none'">
            </div>
            """
        popup_html += f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 12px; border-radius: 8px; margin-bottom: 12px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: white;">
                    {format_price(row['price'], st.session_state.language)}
                </div>
        """
        if st.session_state.language == 'mn':
            usd_price = row['price'] / 3400
            popup_html += f"""
                <div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 4px;">
                    ≈ ${usd_price:,.0f} USD
                </div>
            """
        else:
            mnt_millions = row['price'] / 1_000_000
            popup_html += f"""
                <div style="font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 4px;">
                    ≈ ₮{mnt_millions:.0f}M MNT
                </div>
            """
        popup_html += "</div>"

        popup_html += f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <div style="background: #f3f4f6; padding: 8px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 11px; color: #6b7280;">📐 {t('area')}</div>
                    <div style="font-size: 18px; font-weight: bold; color: #1f2937;">{row['area']:.0f}m²</div>
                </div>
                <div style="background: #f3f4f6; padding: 8px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 11px; color: #6b7280;">🏢 {t('floor')}</div>
                    <div style="font-size: 18px; font-weight: bold; color: #1f2937;">{row['floor']}/{row['building_floor']}</div>
                </div>
            </div>
        """

        popup_html += f"""
            <div style="font-size: 13px; margin-bottom: 10px; padding: 10px; background: #fef3c7; border-radius: 6px;">
                <strong>📍 {t('location')}:</strong><br>
                {row['location']}<br>
                <span style="color: #92400e; font-weight: 600;">{row['district']} {t('district')}</span>
            </div>
        """

        features = []
        if 'balcony_count' in row and row['balcony_count'] not in (None, 'nan'):
            try:
                bc = int(float(row['balcony_count']))
                features.append(f"🌿 {t('balcony_count')}: {bc}")
            except Exception:
                pass
        elif has_feature(row['balcony']):
            features.append(f"🌿 {t('balcony')}: {row['balcony']}")
        if is_elevator_yes(row['elevator']):
            features.append(f"⬆️ {t('elevator')}: {row['elevator']}")
        if has_feature(row['garage']):
            features.append(f"🚗 {t('garage')}: {row['garage']}")
        if row['year'] and row['year'] != 'nan':
            features.append(f"📅 {t('year')}: {row['year']}")
        if row['window_count'] and row['window_count'] != 'nan':
            features.append(f"🪟 {t('window_count')}: {row['window_count']}")

        if features:
            popup_html += f"""
            <div style="font-size: 12px; margin-bottom: 10px; padding: 10px; background: #dbeafe; border-radius: 6px;">
                <strong>{t('features')}:</strong><br>
                {' • '.join(features)}
            </div>
            """

        if row['description'] and row['description'] != 'nan' and len(row['description']) > 10:
            popup_html += f"""
            <div style="font-size: 12px; margin-bottom: 10px; padding: 8px; background: #f9fafb;
                        border-left: 3px solid #3b82f6; max-height: 80px; overflow-y: auto;">
                {row['description']}
            </div>
            """

        meta_items = []
        if row['date'] and row['date'] != 'nan':
            meta_items.append(f"📅 {row['date']}")
        if row['views'] and row['views'] != 'nan':
            meta_items.append(f"👁️ {row['views']} {t('views')}")

        if meta_items:
            popup_html += f"""
            <div style="font-size: 11px; color: #6b7280; margin-bottom: 10px; padding: 8px; background: #f3f4f6; border-radius: 6px;">
                {' • '.join(meta_items)}
            </div>
            """

        if row['link'] and row['link'] != 'nan':
            popup_html += f"""
            <a href="{row['link']}" target="_blank"
               style="display: block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white; padding: 12px; border-radius: 8px; text-decoration: none;
                      font-size: 14px; text-align: center; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                {t('view_on')} →
            </a>
            """

        popup_html += "</div>"

        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{row['title']} - {format_price(row['price'], st.session_state.language)}",
            icon=folium.Icon(
                color=get_marker_color(row['price']),
                icon='home',
                prefix='fa'
            )
        ).add_to(marker_cluster)

    legend_html = f"""
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                z-index: 1000;
                font-family: Arial;">
        <h4 style="margin: 0 0 10px 0; font-size: 14px;">{t('price_legend')}</h4>
        <div style="font-size: 12px;">
            <div style="margin: 5px 0;">
                <span style="color: green; font-size: 16px;">●</span> < ₮200 {t('million')}
            </div>
            <div style="margin: 5px 0;">
                <span style="color: blue; font-size: 16px;">●</span> ₮200-400 {t('million')}
            </div>
            <div style="margin: 5px 0;">
                <span style="color: orange; font-size: 16px;">●</span> ₮400-600 {t('million')}
            </div>
            <div style="margin: 5px 0%;">
                <span style="color: red; font-size: 16px;">●</span> > ₮600 {t('million')}
            </div>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=600)

else:
    st.warning(t('no_results'))

# ------------- PROPERTY LIST WITH PAGINATION -------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader(t('property_list'))

if len(filtered_df) > 0:
    PER_PAGE = 20
    total = len(filtered_df)
    total_pages = (total - 1) // PER_PAGE + 1

    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_df = filtered_df.iloc[start:end]

    st.caption(f"Showing {start+1}-{min(end, total)} of {total} listings")

    for idx, row in page_df.iterrows():
        with st.container():
            st.markdown("""
            <style>
                .property-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                .property-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
                }
                .property-title {
                    color: #1e40af;
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 8px;
                }
                .property-location {
                    color: #6b7280;
                    font-size: 14px;
                    margin-bottom: 12px;
                }
                .property-price {
                    color: #7c3aed;
                    font-size: 32px;
                    font-weight: 700;
                }
                .property-features {
                    display: inline-block;
                    background: #dbeafe;
                    color: #1e40af;
                    padding: 4px 12px;
                    border-radius: 16px;
                    font-size: 12px;
                    margin: 4px 4px 4px 0;
                }
            </style>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if row['image_url'] and row['image_url'] != 'nan':
                    st.image(row['image_url'], use_container_width=True)
                else:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                height: 200px; border-radius: 12px; display: flex;
                                align-items: center; justify-content: center; color: white; font-size: 48px;">
                        🏠
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                if row['link'] and row['link'] != 'nan':
                    title_html = f"<a href='{row['link']}' target='_blank' class='property-title' style='text-decoration:none;'>{row['title']}</a>"
                else:
                    title_html = f"<div class='property-title'>{row['title']}</div>"
                st.markdown(title_html, unsafe_allow_html=True)

                st.markdown(
                    f"<div class='property-location'>📍 {row['location']} • {row['district']}</div>",
                    unsafe_allow_html=True
                )

                detail_cols = st.columns(4)
                with detail_cols[0]:
                    st.markdown(f"**📐 {row['area']:.0f}m²**")
                with detail_cols[1]:
                    st.markdown(f"**🏢 {row['floor']}/{row['building_floor']}**")
                with detail_cols[2]:
                    if row['year'] and row['year'] != 'nan':
                        st.markdown(f"**📅 {row['year']}**")
                with detail_cols[3]:
                    if row['window_count'] and row['window_count'] != 'nan':
                        st.markdown(f"**🪟 {row['window_count']}**")

                features_html = ""
                if 'balcony_count' in row and row['balcony_count'] not in (None, 'nan'):
                    features_html += f"<span class='property-features'>🌿 {t('balcony_count')}</span>"
                elif has_feature(row['balcony']):
                    features_html += f"<span class='property-features'>🌿 {t('balcony')}</span>"
                if is_elevator_yes(row['elevator']):
                    features_html += f"<span class='property-features'>⬆️ {t('elevator')}</span>"
                if has_feature(row['garage']):
                    features_html += f"<span class='property-features'>🚗 {t('garage')}</span>"

                if features_html:
                    st.markdown(features_html, unsafe_allow_html=True)

                if row['description'] and row['description'] != 'nan' and len(row['description']) > 10:
                    with st.expander("📝 " + t('description')):
                        st.write(row['description'])

            with col3:
                st.markdown(
                    f"<div class='property-price'>{format_price(row['price'], st.session_state.language)}</div>",
                    unsafe_allow_html=True
                )
                if st.session_state.language == 'mn':
                    usd = row['price'] / 3400
                    st.caption(f"≈ ${usd:,.0f} USD")
                else:
                    mnt_millions = row['price'] / 1_000_000
                    st.caption(f"≈ ₮{mnt_millions:.0f}M MNT")
                if row['date'] and row['date'] != 'nan':
                    st.markdown(f"📅 {row['date']}")
                if row['views'] and row['views'] != 'nan':
                    st.markdown(f"👁️ {row['views']} {t('views')}")
                if row['link'] and row['link'] != 'nan':
                    st.link_button("🔗 " + t('view_on'), row['link'], use_container_width=True)

            st.divider()

    st.caption(f"Page {page} of {total_pages}")

else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fcd34d 100%);
                padding: 40px; border-radius: 16px; text-align: center; margin: 40px 0;">
        <div style="font-size: 64px; margin-bottom: 20px;">🔍</div>
        <h2 style="color: #92400e; margin-bottom: 16px;">No Properties Found</h2>
        <p style="color: #78350f; font-size: 16px;">Try adjusting your filters to see more results</p>
        <div style="margin-top: 24px; color: #78350f;">
            <strong>Tips:</strong><br>
            • Expand the price range<br>
            • Select more districts<br>
            • Adjust the year range<br>
            • Change feature filters to "Any"
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #6b7280;">
    <p style="font-size: 14px;">🏠 Built with Streamlit + Folium | Real data from unegui.mn</p>
    <p style="font-size: 12px; margin-top: 8px;">© 2024 Ulaanbaatar Real Estate Map | All rights reserved</p>
</div>
""", unsafe_allow_html=True)
